import contextlib
from functools import wraps
from logger import logger, toaster

import threading
import time

import pyperclip
import azure.cognitiveservices.speech as speechsdk

from PIL import ImageGrab
import pytesseract

import pyautogui
import custom_keyboard
from pynput import mouse, keyboard
import autoit   ##### TO isntall it uses pip install pyautoit

import ctypes
import ctypes.wintypes as wintypes
from ctypes.wintypes import DWORD, HWND

from pywinauto.application import Application, ProcessNotFoundError
import psutil
import os

# Ctypes Stuff
WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

EnumWindows = ctypes.WinDLL('user32').EnumWindows
EnumWindows.argtypes = WNDENUMPROC, wintypes.LPARAM  # LPARAM not INT
EnumWindows.restype = wintypes.BOOL

GetWindowText = ctypes.WinDLL('user32').GetWindowTextW
GetWindowTextLength = ctypes.WinDLL('user32').GetWindowTextLengthW

IsWindow = ctypes.WinDLL('user32').IsWindow

GetWindowThreadProcessId = ctypes.WinDLL('user32').GetWindowThreadProcessId
ctypes.WinDLL('user32').GetWindowThreadProcessId.restype = wintypes.DWORD
ctypes.WinDLL('user32').GetWindowThreadProcessId.argtypes = (
        wintypes.HWND,     # _In_      hWnd
        wintypes.LPDWORD,) # _Out_opt_ lpdwProcessId

GetForegroundWindow = ctypes.WinDLL('user32').GetForegroundWindow


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
logger.debug(VDA)

# Setting up the speech config
try:
    with open(r'C:\Coding\azure_speech_config.txt', 'r') as f:
        contents = f.read()
        contents = contents.split(', ')
        SPEECH_KEY, SPEECH_REGION = contents

    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    # The language of the voice that speaks.
    speech_config.speech_synthesis_voice_name='en-US-JennyNeural'
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

except Exception as e:
    logger.error(f'Error setting up speech config: {e}')
    toaster.show_toast("Speech Config Error", "See Log File for more information", duration=5, threaded=True)

"""
A bunch of utillity functions
"""

#############################################     These are tools    #############################################
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

# def filter_process_list(process_to_find: str, process_list):
#     """         loops thru the list to find processes with name you want        \n
#     Returns list of dictionarys containing processes with process_to_find in name \n
#     Returns empty list if there are none
#     """
#     logger.debug("filter_process_list")
#     return [
#             proc 
#             for proc in process_list
#             if process_to_find.lower() in proc['Title'].lower()
#             ]

def perform_hotkey(hotkey):
    #logger.debug(f"perform_hotkey {hotkey = }")
    custom_keyboard.hotkey(*hotkey)

def perform_press(key):
    #logger.debug(f"perform_press {key = }")
    custom_keyboard.press(key)

def get_processes():
    """Returns list of dictionarys of all apps, their PIDS and hwnd\n
    """

    @WNDENUMPROC
    def py_callback( hwnd, lparam ):
        pid = wintypes.DWORD()
        tid = GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if IsWindow(hwnd):
            length = GetWindowTextLength(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            GetWindowText(hwnd, buff, length + 1) 

            if buff.value and buff.value not in ['Default IME', 'MSCTFIME UI']:
                results.append({"Title": buff.value,
                                "TID": tid,
                                "HWND": hwnd,
                                "PID": pid.value})
        return True

    results = []
    EnumWindows(py_callback,0)

    return results

def get_focused():
    hwnd = GetForegroundWindow()
    length = GetWindowTextLength(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    GetWindowText(hwnd, buff, length + 1)

    return buff.value or None

def pidGetter(name: str)-> int: 
    """
    Returns the PID of the parent Process you want.

    Put in the name of the app you want a PID from as a string.
    
    And you will get the PID of the parent proccess as an int.
    """
    PID = None
    for p in psutil.process_iter(['name']):
        if name in p.info['name']:
            parent = p.parent()
            if parent is not None:
                PID = parent.pid
                break
    return PID

def hwndGetter(app_name: str) -> HWND:
    """Returns the hwnd of the app you specified
    This returns the  first valid one, so it might not work for chrome
    Returns None if there is nothing.

    Args:
        app_name (str): The name of the app.

    Returns:
        HWND: the HWND of the app.
    """
    processes = get_processes()
    for process in processes:
        if app_name in process['Title']:
            return process['HWND']

def launchApp(name_or_path:str, timeout:int = 0.5) -> None:
    #logger.debug(name_or_path,timeout)
    try:
        os.startfile(name_or_path)
    except Exception as e:
        logger.warning(e)
    time.sleep(timeout)

#############################################     These use VirtualDesktopAccessor.dll    #############################################
# def GetWindowHwndFromPid(pid):
#     """
#     This code is from here: #https://stackoverflow.com/questions/60879235/python-windows-10-launching-an-application-on-a-specific-virtual-desktop-envir
#     I can sort of understand it, so I wont explain it.
#     """
        
#     current_window = 0
#     pid_local = DWORD()
#     while True:
#         # current_window = windll.User32.FindWindowExA(0, current_window, 0, 0)
#         # windll.user32.GetWindowThreadProcessId(current_window, byref(pid_local))
#         ctypes.WinDLL('user32').GetWindowThreadProcessId(current_window, ctypes.byref(pid_local))
#         ctypes.WinDLL('user32').FindWindowExA(0, current_window, 0, 0)
        

        
#         #GetWindowThreadProcessId(current_window, ctypes.byref(pid_local))
#         logger.debug(current_window)
                
#         if pid == pid_local.value:
           
#             yield current_window
#             #yield current_window

#         if current_window == 0:
#             return

# def GetParentsFromList(windows: list) -> HWND:
#     """
#     Returns the parent HWND of a list of HWND
#     """
#     parents = []
#     for window in windows:
#         parent = GetParent(window)
#         #print(window, parent)
#         if parent != 0:
#             parents.append(parent)

#     return parents

# def IsWindowOnDesktop(hwnd: HWND) -> bool:
#     """
#     Returns a Bool of is the HWND if on the CurrentVirtualDesktop
#     """
#     return  bool(virtual_desktop_accessor.IsWindowOnCurrentVirtualDesktop(hwnd))

# def MoveAppToCurrentDesktop(hwnd: HWND):
#     current_window = CurrentDesktopNumber()

#     if not IsWindowOnDesktop(hwnd): # that app is not on current desktop
#         virtual_desktop_accessor.MoveWindowToDesktopNumber(hwnd, current_window)


###############     These are all macros     ###############

def sheild_focus_star_citizen(key): #macro to focus ship shields in star citizen
    logger.debug(f"right shift + {key}")
    # custom_keyboard.hotkey('shiftright', key)
    # time.sleep(0.1)
    # custom_keyboard.press('shiftright')

    perform_hotkey(['shiftright', key])
    time.sleep(0.1)
    perform_press('shiftright')

def rocket_flying():# Rocket Flying Test
    # https://www.youtube.com/watch?v=ItN-K-WSCkM
    #currently it only works if your looking straight up.
    logger.debug("Rocket Flying Test")
    autoit.mouse_click()
    perform_press('q')
    
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

    #print(repr(text))
    #Formats the text

    # text1 = text.replace("\r\n\r\n", "")

    # text2 = text1.split(". ")

    # text3 = [f'{i}.' for i in text2 if i != '']

    # logger.debug(text3)
    # for i in text3:
    #     if len(i) > 1:
    #         speech_synthesis_result = speech_synthesizer.speak_text_async(i)
    #         time.sleep(0.2)

    # #Old Formating
    # #print(repr(good_text))
    # cleaned_text = text.replace("\r\n", " ")    
    # good_text = cleaned_text.split(". ")
    # logger.debug(good_text)

    # for i in good_text:
    #     if len(i) > 1:
    #         speech_synthesis_result = speech_synthesizer.speak_text_async(i)

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
    if VDA:
        if direction == 'left':
            newDesktopNum = CurrentDesktopNumber() -1
        elif direction == 'right':
            newDesktopNum = CurrentDesktopNumber() + 1
        GoToDesktop(newDesktopNum)
    else:
        apps_to_alt_tab = ['Star Citizen']  #lis of apps to alt tab when changing desktops

        if focused_app in apps_to_alt_tab: 
            perform_hotkey(['alt', 'tab'])
            #custom_keyboard.hotkey('alt', 'tab')
            time.sleep(0.1)

        perform_hotkey(['ctrl', 'win', direction])


def moveSpotifyAccrossDesktops(name:str, movement: str)-> None:
    """This just gets Spotify's HWND, Spotify's title changes  to the song that is playing, so that makes it more difficult to filter it out.

    Args:
        name (str): _description_
        movement (str): _description_
    """
    
    hwnd = hwndGetter(name)
    if hwnd is None:
        logger.debug('either spotify is not running or a song is playing.')
        PID = pidGetter('Spotify')
        if PID is None:
            logger.debug('Spotify is not running')
            launchApp('Spotify', timeout=1)
            moveSpotifyAccrossDesktops(name, movement)
        
        processes = get_processes()

        for process in processes:
            if process['PID'] == PID:
                hwnd = process['HWND']
                logger.debug(f"found the {hwnd=}")
                break
    moveAppAccrossDesktops(hwnd, movement)
    
def moveAppAccrossDesktops(hwnd_or_name: HWND|str, movement: str) -> int:
    """Moves an app accross desktops.
    This function requires the VirtualDesktopAccessor.dll, if it is not installed, the  func will return -1
    If you input and app name, it will try and get the hwnd
    if the app is not active, the hwnd will be None and the func will return -2
    
    Movements are:
    'Left': Goes left,
    'Right': Goes Right,
    'Current': Moves to the current desktop
    
    Args:
        hwnd_or_name (HWND | str): Either the name of the app or the HWND of the app
        movement (str): Movement Type

    Returns:
        bool: It will return 1 if succesfull and 0 if not
    """
    if not VDA:
        msg = r"""VirtualDesktopAccessor.dll Cannot be found. This function will not work without it
        You can find it here: https://github.com/Ciantic/VirtualDesktopAccessor?tab=readme-ov-file, make sure you download the correct version for your operating system. \nPut it in "C:\Windows\System32" """
        logger.warning(msg)
        return -1
    logger.debug(hwnd_or_name)
    
    if isinstance(hwnd_or_name,  str):
        hwnd = hwndGetter(hwnd_or_name)
        if hwnd is None:
            logger.debug("hwnd is None")
            #launchApp(hwnd_or_name)
            return
    else:
        hwnd = hwnd_or_name    
        
    logger.debug(hwnd)
    
    movements = {
        'Left': (GetWindowDesktopNumber(hwnd) -1),
        'Right': (GetWindowDesktopNumber(hwnd) +1),
        'Current': CurrentDesktopNumber()
        }

    destination = movements[movement]
    return MoveAppToDesktop(hwnd, destination) 

""" 
this is a new way to controll spotify and chrome.
The spotifyControlTest alloys me to the same stuff as before, but also contol the volume of audio coming from spotify

chromeAudioControlTest allows me to play pause yt videos.

Maybe redo mediaTimerV1, for like a button timer, IDK
"""

def mediaTimerV2(destination: str, timeout = 0.4, count=[0]):  # this is basically the same as spotifyV3
    """Plays/Pauses media, presses next song previous song.   
    
    Press 1 time in timeout seconds to Plays/Pauses.        \n
    Press 2 times in timeout seconds to get next song.      \n
    Press 3 times in timeout seconds to get previous song.  \n   

    Args:
      timeout (integer): Defines how much time you have to press the button for it to do something
      count (list): Don't touch this, it is a counter for the function
    Returns:
      None
    """
    count[0] += 1
    
    logger.debug("Media Func Has been called")
    
    def timerV4():
        """Waits for timeout to finish then it send a keyboard input based on value of count[0]"""

        logger.debug("timer Has just begun")
        time.sleep(timeout)
        logger.debug("timer sleep has just finished")
        runAfterTimer()
        

    def runAfterTimer():
        
        ACTIONS = [
            "PlayPause",
            "NextTrack",
            "PrevTrack"]
        
        DESTINATIONS = {
            'Spotify': spotifyControl,
            'Chrome': chromeAudioControl
        }
        
        logger.debug("Entering try")
        try:
            action = ACTIONS[count[0]-1]
            logger.debug(f'Value of {count[0] = }, executing folowing action: {action}')
            functionToCall = DESTINATIONS[destination]
            functionToCall(action)
            

        except IndexError as ind:
            logger.error(f'IndexError has just happened, reason: {ind}')
            logger.error(f'Button was pressed to many times. You pressed it {count[0]} times.\n')

        except Exception as e:
            logger.error(e)
        
        finally:
            count[0] = 0
            logger.debug(f"Value of {count[0] = }\n")

    """         Finds if thread I want is running, if not it starts, if it is does nothing          """
    # adds True to list if func hmm is running as a thread
    thread_running = [
        True
        for thread in threading.enumerate()
        if timerV4.__name__ in thread.name
        ]
    
    if not any(thread_running):
        logger.debug("Thread I want is not running, starting it")
        media_thread = threading.Thread(target=timerV4, args=(),daemon=True)
        media_thread.start()
    else:
        logger.debug("thread I want is running")

spotify_PID = False
Chrome_Parent_PID = False
##Controlls Spotify
def spotifyControl(action):
    """Uses pywinauto to connect and send keystrokes to Spotify.    

    These are the available actions:
     - "VolumeUp"
     - "VolumeDown"
     - "PrevTrack"
     - "NextTrack"
     - "PlayPause"
     - "Back5s"
     - "Forward5s"
     - "Like"

    To use simply:

    spotifyControl("PrevTrack")
    """
    logger.debug("in spotifyControlTest")
    
    SPOTIFY_HOTKEYS = {
        "VolumeUp": "^{UP}",
        "VolumeDown": "^{DOWN}",
        "PrevTrack": "^{LEFT}",
        "NextTrack": "^{RIGHT}",
        "PlayPause": "{SPACE}",
        "Back5s": "+{LEFT}",
        "Forward5s": "+{RIGHT}",
        "Like": "%+{B}",
        "Quit": "",
    }

    """
    How this is currently setup, the little media player popup doesnt show up. so it I dont know what the song is.    
    That would mean I wouldnt need modern flyouts.
    """
    global spotify_PID
    if spotify_PID is False:
        logger.debug("spotify_PID is False")
        PID = pidGetter('Spotify')
        if PID is None:
            print('There is no app with name of "Spotify"')
            launchApp('Spotify')
            spotifyControl(action)
            #return
        spotify_PID = PID
    
    
    #print(spotify_PID)

    #https://github.com/mavvos/SpotifyGlobal/blob/main/SpotifyGlobal.py#L118
    try:
        app = Application().connect(process=spotify_PID)
        
        spotify = app["Chrome_Widget_Win0"]
        spotify.send_keystrokes(SPOTIFY_HOTKEYS[action])
        # spotify.send_keystrokes(SPOTIFY_HOTKEYS["PlayPause"])
        # spotify.send_keystrokes(SPOTIFY_HOTKEYS["Forward5s"])
        # spotify.send_keystrokes(SPOTIFY_HOTKEYS["PlayPause"])

    except ProcessNotFoundError: #### Will have to modify this, so that it checks if spotify is running. 
        logger.warning('Process was not Found')

        PID = pidGetter('Spotify')
        if PID is None:
            logger.debug('There is no app with name of "Spotify"')
            launchApp('Spotify', timeout=1)
            spotify_PID = False
            
        else:
            logger.debug("had the wrong PID")
            spotify_PID = PID
            
        spotifyControl(action)

def chromeAudioControl(action):
    """Uses pywinauto to connect and interact with chromes media controls   

    These are the available actions:
     - "PrevTrack"
     - "NextTrack"
     - "PlayPause"

    To use simply:

    chromeAudioControl("PrevTrack")

    This code assumes that the audio source you want to interact with was the last one you used
    / is first in Global Media Controls.
    
    If there is nothing in the Global Media Controls this will do nothing.

    If you click something else while it does its thing it will break.
    """
    logger.debug("In chromeAudioControlTest")
    # ### inspector C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64
    # Chrome_Parent_PID = []

    """
    I could probably switch this to hwndGetter('Chrome')
    to stop using  pidGetter('chrome')
    
    """
    
    
    global Chrome_Parent_PID
    if Chrome_Parent_PID is False:
        logger.debug("Chrome_Parent_PID is False")
        PID = pidGetter('chrome')
        if PID is None:
            print('There is no app with name of "Spotify"')
            return
        Chrome_Parent_PID = PID

    logger.debug("Got PID")

    app = Application(backend="uia").connect(process=Chrome_Parent_PID)

    logger.debug("Connected to Chrome")

    media_control_button = app.window().child_window(title="Control your music, videos, and more", control_type="Button")
    logger.debug("got media_control_button")
    try:
        media_control_button.click()
    except Exception as e:
        print(e)
        print("There is nothing in the Global Media Controls")
        return 

    #time.sleep(0.1)

    ### this skips right to it
    last_video_media_control = app.window().child_window(title="Back to tab", control_type="Button", found_index=0)
    media_controls = last_video_media_control.children()

    logger.debug("got media_controls")

    actions = {
        'PrevTrack': 1,
        'SeekBackward': 2,
        'PlayPause': 3,
        'SeekForward': 4,
        'NextTrack': 5}
    
    num = actions[action]

    if len(media_controls) == 9:
        num += 1
    media_controls[num].click()

    logger.debug(f"pressed media_controls {actions[action]}")

    media_control_button.click()
    logger.debug("Closed tab")
