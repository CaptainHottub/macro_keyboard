import contextlib
from functools import wraps
from setup import logger, send_notification

import time
import pyperclip
import azure.cognitiveservices.speech as speechsdk
from PIL import ImageGrab
import pytesseract
import pyautogui
from pynput import mouse, keyboard
import os
import sys

logger.debug(f'Initializing {__file__}')

from media_controllers import _moveAppAccrossDesktops as moveAppAccrossDesktops
#from media_controllers import get_focused
plat = sys.platform

if sys.platform == 'win32':
    import custom_keyboard
    import autoit
    import win32gui
    import win32process
    import ctypes

    r"""
    VirtualDesktopAccessor.dll is used to move apps between virtual desktops:  https://github.com/Ciantic/VirtualDesktopAccessor?tab=readme-ov-file
    This is a safety feature, if VirtualDesktopAccessor.dll isn't in "C:\Windows\System32" it will disable any func that uses it.
    """
    try:
        virtual_desktop_accessor = ctypes.WinDLL("VirtualDesktopAccessor.dll")
        CurrentDesktopNumber = virtual_desktop_accessor.GetCurrentDesktopNumber
        #DesktopCount = virtual_desktop_accessor.GetDesktopCount
        GoToDesktop = virtual_desktop_accessor.GoToDesktopNumber
        MoveAppToDesktop = virtual_desktop_accessor.MoveWindowToDesktopNumber # requires (hwnd, desktop_num)
        #IsWindowOnDesktopNumber = virtual_desktop_accessor.IsWindowOnDesktopNumber #hwnd: HWND, desktop_number: i32
        GetWindowDesktopNumber = virtual_desktop_accessor.GetWindowDesktopNumber          # (hwnd: HWND)
        
    except FileNotFoundError as e:
        print(e)
        VDA = False
    else:
        VDA = True
    #logger.debug(f"{VDA=}")

    def _get_processes_win32(filter=['Default IME', 'MSCTFIME UI'], sortby='Title')-> list[dict]:
        """Returns list of dictionarys of all apps, their PIDS and hwnd\n
        
        by default it will remove any blank handle, and any handle with any name defined in filter.
        by default it will sort the list by title, but you can specify it for any key in the returned list
        
        returns: 
            [{"Title": windowtitle,
            "TID": threadid,
            "HWND": hwnd,
            "PID": pid}]
        """
        def py_callback(hwnd, lparam):
            threadid, pid = win32process.GetWindowThreadProcessId(hwnd)
                    
            if win32gui.IsWindow(hwnd):
                windowtitle = win32gui.GetWindowText(hwnd)
                
                if windowtitle and windowtitle not in filter:
                    results.append({"Title": windowtitle,
                                "TID": threadid,
                                "HWND": hwnd,
                                "PID": pid})
        
            return True

        results = []
        win32gui.EnumWindows(py_callback,0)
        
        if sortby:
            results = sorted(results, key=lambda d: d[sortby])
        
        return results

    def _get_focused_win32():
        hwnd = win32gui.GetForegroundWindow()
        return win32gui.GetWindowText(hwnd), hwnd

    def _get_forground_hwnd():
        processes = _get_processes_win32()
        for process in processes:
            if process['Title'] == 'Program Manager':
                return process['HWND']
        
        return None
    
    get_processes = _get_processes_win32
    get_focused = _get_focused_win32
    
    forground_hwnd = _get_forground_hwnd()
    
    logger.debug(f'Succesfully setup {plat} specific functions')

elif sys.platform == 'linux':
    import pyautogui as custom_keyboard
    logger.warning("custom_keyboard has been redirectd to Pyautogui")
    logger.warning("autoit is disabled")

    # def _get_processes_linux()-> list[dict]:
    #     """Returns list of dictionarys of all apps, their PIDS and hwnd\n
        
    #     by default it will remove any blank handle, and any handle with any name defined in filter.
    #     by default it will sort the list by title, but you can specify it for any key in the returned list
        
    #     returns: 
    #         [{"Title": windowtitle,
    #         "TID": threadid,
    #         "HWND": hwnd,
    #         "PID": pid}]
    #     """
    #     #raise NotImplementedError
    #     ...

    # def _get_focused_linux():
        #raise NotImplementedError
        #...
    
    VDA = False

    # get_processes = _get_processes_linux()
    # get_focused = _get_focused_linux()  
    logger.debug(f'Succesfully setup {plat} specific functions')
    
# Setting up the speech config

try:
    # the keys are stored in the environment variables
    SPEECH_KEY = os.environ.get('AZURE_SPEECH_KEY')
    SPEECH_REGION = os.environ.get('AZURE_SPEECH_REGION')
    if SPEECH_KEY is None or SPEECH_REGION is None:
        raise ValueError("One of the AZURE_SPEECH_KEYS is not defined.", (SPEECH_KEY,SPEECH_REGION))
    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    # The language of the voice that speaks.
    speech_config.speech_synthesis_voice_name='en-US-JennyNeural'
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

except Exception as e:
    logger.error(f'Error setting up speech config: {e}')
    #toaster.show_toast("Speech Config Error", "See Log File for more information", duration=5, threaded=True)
    send_notification(title='Speech Config Error', msg='Speech Config Error\nSee Log File for more information', expire_time=2, urgency='normal')

"""
A bunch of utillity functions
"""

#############################################     These are tools  IDK WHY ITS CALLED THIS   #############################################
# timer function
def get_time(func):
    """Times any function\n
    Use as decorator to time funcs\n
    @get_time """

    @wraps(func)
    def timer(*args, **kwargs):
        start_time = time.perf_counter()
        
        func(*args, **kwargs)

        end_time = time.perf_counter()
        total_time = round(end_time - start_time, 6)

        func_name = func.__name__
        logger.info(f'{func_name} took {total_time} seconds to complete')
    
    return timer

def perform_hotkey(hotkey):
    #logger.debug(f"perform_hotkey {hotkey = }")
    custom_keyboard.hotkey(*hotkey)

def perform_press(key):
    #logger.debug(f"perform_press {key = }")
    custom_keyboard.press(key)

def libreOffice_zoomin():
    custom_keyboard.keyDown('ctrl')
    pyautogui.hscroll(10)
    custom_keyboard.keyUp('ctrl')

def libreOffice_zoomout():
    custom_keyboard.keyDown('ctrl')
    pyautogui.hscroll(-10)
    custom_keyboard.keyUp('ctrl')

# def pidGetter(name: str)-> int: 
#     """
#     Returns the PID of the parent Process you want.

#     Put in the name of the app you want a PID from as a string.
    
#     And you will get the PID of the parent proccess as an int.
#     """
#     PID = None
#     for p in psutil.process_iter(['name']):
#         if name in p.info['name']:
#             parent = p.parent()
#             if parent is not None:
#                 PID = parent.pid
#                 break
#     return PID

# def launchApp(name_or_path:str, timeout:int = 0.5) -> None:
#     #logger.debug(name_or_path,timeout)
#     try:
#         os.startfile(name_or_path)
#     except Exception as e:
#         logger.warning(e)
#     time.sleep(timeout)


###############     These are all macros     ###############

def sheild_focus_star_citizen(key): #macro to focus ship shields in star citizen
    logger.debug(f"right shift + {key}")
    # custom_keyboard.hotkey('shiftright', key)
    # time.sleep(0.1)
    # custom_keyboard.press('shiftright')

    perform_hotkey(['shiftright', key])
    time.sleep(0.1)
    perform_press('shiftright')

# def rocket_flying():# Rocket Flying Test
#     # https://www.youtube.com/watch?v=ItN-K-WSCkM
#     #currently it only works if your looking straight up.
#     logger.debug("Rocket Flying Test")
#     autoit.mouse_click()
#     perform_press('q')
    
def wellskate(): #wellskate
    """ Performs the wellskate macro for destiny 2"""
    logger.debug("Wellskate")
    perform_press('3')
    time.sleep(0.5)
    pyautogui.click(button='right')
    perform_hotkey(['space', 'f'])
    time.sleep(0.1)
    perform_press('1')

def Image_to_text2():
    """Presses Win Shift S to open snippet mode, waits for mouse release then does tesseract OCR
    Press Ctrl V to paste text
    """

    logger.debug("imt has just started")

    m = mouse.Controller()

    def on_release(key):
        if key == keyboard.Key.esc:
            logger.debug('esc pressed and released')
            # Stop listener and the func
            m.click(mouse.Button.left,1)
            return False

    keyboard_listener = keyboard.Listener(
        on_release=on_release)
    
    perform_hotkey(['winleft', 'shift', 's'])
    #custom_keyboard.hotkey('winleft', 'shift', 's')
    time.sleep(0.2)

    keyboard_listener.start()

    mouse_clicks = []   
                
    with mouse.Events() as events:
        for event in events:
            with contextlib.suppress(Exception):
                if event.button == mouse.Button.left:
                    text = {
                        'x': event.x,
                        'y': event.y,
                        'button': str(event.button),
                        'pressed': event.pressed}
                    mouse_clicks.append(text)
                    if not event.pressed:
                        break
    
    pressed =  keyboard_listener.is_alive()
    if not pressed:
        print("keyboard_listener is not running")
        return False
    
    #checks if the mouse moved
    click1, click2 = mouse_clicks
    dx = click1['x'] - click2['x']
    dy = click1['y'] - click2['y']
    if dx == 0 and dy == 0:
        print("mouse didnt move")
        return False
    
    time.sleep(0.1)
    
    # grabs the image from clipboard and converts the image to text.
    img = ImageGrab.grabclipboard()
    text = pytesseract.image_to_string(img)
    text = text.replace('\x0c', '')
    pyperclip.copy(text)
    logger.debug("imt has finished")

def ButtonMode(mode):
    ButtonDescriptions = f"""Current mode is: {mode}
    If button is not their nothing is assigned to it.
        
    Default/Mode 1/Works on any mode and unspecified app:
        Button 1:   Shows this
        Button 2:   Controls spotify: Acts like headphone controls.
        Button 3:   Switches desktop to the left
        Button 4:   Switches desktop to the right
        Button 5:   Text to speech, Converts highlighted text to speech
        Button 6:   Stop Speech
        Button 7:   Copy
        Button 8:   Paste
        Button 9:   Search highlighted text
        Button 10:  Opens Task Manager
        Button 11:  Converts image to text

    When in Vscode:
        Button 5:   run code in Vs code
	
    When in Destiny 2:
        Button 5: Rocket Flying Test 
        Button 6: Wellskate Test

    When in Star Citizen:
        Button 5: focus front shields  
        Button 6: focus back shields
        Button 7: Reset shields

    Mode 2:
        Button 5: Cut (ctrl +x)
        Button 6: Split/Italics (Ctrl + i) 
        Button 9: Backspace
        
    Mode 3 and 4 do nothing
    """
    pyautogui.alert(ButtonDescriptions, "Button Mode")  


# I could probably swap Azure for pyttsx3 
def textToSpeech():
    logger.info("in textToSpeech")
    """Microsoft Azure moves to TLS 1.2 On October 31 2024
    IDK what that really means, so if this breaks after that date, we will know why
    https://learn.microsoft.com/en-us/security/engineering/solving-tls1-problem
    """
    perform_hotkey(['ctrl', 'c'])
    time.sleep(0.1)
    text = pyperclip.paste()


    speech_synthesizer.speak_text(text)

    #speech_synthesis_result = speech_synthesizer.speak_text_async(text)

def stopSpeech():
    logger.info("in stopSpeech")
    speech_synthesizer.stop_speaking()
    #speech_synthesizer.stop_speaking_async()

def search_highlighted_text():
    """Searches highlighted text in google.
    
    Copies highlighted text, opens new tab, pastes text, presses enter."""
    logger.debug("in search_highlighted_text")
    perform_hotkey(['ctrl', 'c'])

    time.sleep(0.1)

    perform_hotkey(['ctrl', 't'])
    time.sleep(0.2)

    perform_hotkey(['ctrl', 'v'])
    time.sleep(0.2)
    
    perform_press('enter')


def change_desktop(direction, focused_app): #change desktop hotkey, where direction is either 'left' or 'right'. Will alt+tab if specific program is focused
    """
    The VDA one take on average 5 ms to complete, IT also doesn't need to alt tab some apps like task manager
    while the other one takes 100 ms to complete
    """
    logger.debug(f"move desktop {direction}")
    if VDA and sys.platform == 'win32':
        # processes = get_processes()
        # for process in processes:
        #     if process['Title'] == 'Program Manager':
        #         win32gui.SetForegroundWindow(process['HWND'])
        # global forground_hwnd
        
        # if not forground_hwnd:
        #     processes = get_processes()
        #     for process in processes:
        #         if process['Title'] == 'Program Manager':
        #             forground_hwnd = process['HWND']
        
        # win32gui.SetForegroundWindow(forground_hwnd)
        # this is iff for somereason it doesn't work
        
        #### this is so much faster!!!!
        try: 
            global forground_hwnd
            win32gui.SetForegroundWindow(forground_hwnd)
        except Exception as e:
            print(e)
            if isinstance(e, win32gui.error):
                #It's not actually a win32gui error, its from pywintypes.error, and win32gui imports it as error.
                forground_hwnd = _get_forground_hwnd()

        
        if direction == 'left':
            newDesktopNum = CurrentDesktopNumber() -1
        elif direction == 'right':
            newDesktopNum = CurrentDesktopNumber() + 1
        

        GoToDesktop(newDesktopNum)
    
    else:

        if plat == 'win32':
            apps_to_alt_tab = ['Star Citizen']  #lis of apps to alt tab when changing desktops

            if focused_app in apps_to_alt_tab: 
                perform_hotkey(['alt', 'tab'])
                #custom_keyboard.hotkey('alt', 'tab')
                time.sleep(0.1)
        
            perform_hotkey(['ctrl', 'win', direction])

        elif plat == 'linux':
            
            if direction == 'left':
                cmd = 'xdotool set_desktop --relative -- -1'
            elif direction == 'right':
                cmd = 'xdotool set_desktop --relative -- 1'
            os.system(cmd)


# def moveAppAccrossDesktops(hwnd: int, movement: str) -> int:
#     """Moves an app accross desktops.
#     This function requires the VirtualDesktopAccessor.dll, if it is not installed, the  func will return 1
#     If you input an app name, it will try and get the hwnd
#     if the app is not active, the hwnd will be None and the func will return 0
    
#     Movements are:
#     'Left': Goes left,
#     'Right': Goes Right,
#     'Current': Moves to the current desktop
    
#     Args:
#         hwnd (HWND): The HWND(handle) of the app
#         movement (str): Movement Type

#     Returns:
#         bool: It will return 1 if succesfull and 0 if not
#     """
#     if VDA and sys.platform == 'win32':
#         #logger.debug(hwnd)
        
#         if hwnd is None:
#             logger.debug("hwnd is None")
#             #launchApp(hwnd)
#             return 0
        
#         movements = {
#             'Left': (GetWindowDesktopNumber(hwnd) -1),
#             'Right': (GetWindowDesktopNumber(hwnd) +1),
#             'Current': CurrentDesktopNumber()
#             }

#         destination = movements[movement]
#         return MoveAppToDesktop(hwnd, destination) 
    
#     else:
#         msg = r"""VirtualDesktopAccessor.dll Cannot be found. This function will not work without it
#         You can find it here: https://github.com/Ciantic/VirtualDesktopAccessor?tab=readme-ov-file, make sure you download the correct version for your operating system. \nPut it in "C:\Windows\System32" """
#         logger.warning(msg)
#         return 1


logger.debug(f"Initializing is complete for {__file__}")