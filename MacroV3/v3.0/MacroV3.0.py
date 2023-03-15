import contextlib
import pystray
import serial.tools.list_ports
import sys
import custom_keyboard
import datetime
import threading
import pyautogui
import os
import pyperclip
import win32gui
import logging
import time

import azure.cognitiveservices.speech as speechsdk

from PIL import Image, ImageGrab
from win10toast import ToastNotifier

import pytesseract
from pynput import mouse, keyboard
import autoit
# from pywinauto import Application
# import win32process
# import psutil

# import ctypes
# import ctypes.wintypes as wintypes

# # Ctypes Stuff
# WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

# EnumWindows = ctypes.WinDLL('user32').EnumWindows
# EnumWindows.argtypes = WNDENUMPROC, wintypes.LPARAM  # LPARAM not INT
# EnumWindows.restype = wintypes.BOOL

# GetWindowText = ctypes.WinDLL('user32').GetWindowTextW
# GetWindowTextLength = ctypes.WinDLL('user32').GetWindowTextLengthW

# IsWindow = ctypes.WinDLL('user32').IsWindow

# GetWindowThreadProcessId = ctypes.WinDLL('user32').GetWindowThreadProcessId
# ctypes.WinDLL('user32').GetWindowThreadProcessId.restype = wintypes.DWORD
# ctypes.WinDLL('user32').GetWindowThreadProcessId.argtypes = (
#         wintypes.HWND,     # _In_      hWnd
#         wintypes.LPDWORD,) # _Out_opt_ lpdwProcessId


#Script directory
script_path = os.path.dirname(os.path.abspath(__file__))
log_folder_path = r'C:\Users\Taylor\Desktop\Macro Logs'

def log_folder(log_folder_path):
    """Returns path to log folder with version name.\n
    Will create a folder at that path location.
    
    Define log_folder_path as the path of the log folder you want.
    """
    script_path = os.path.dirname(os.path.abspath(__file__))

    version = script_path.split('\\')[-1]
    version = version.upper()
        
    log_folder = f'{log_folder_path}\{version}'

    if os.path.isdir(log_folder):
        return log_folder
    os.mkdir(log_folder)

    return log_folder

#Custom logger format, 
class CustomFormatter(logging.Formatter):
    MAGENTA = "\u001b[35m"
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = '%(asctime)s.%(msecs)03d %(levelname)s - %(funcName)s: %(message)s'

    FORMATS = {
        logging.DEBUG: MAGENTA + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt='%H:%M:%S')
        return formatter.format(record)

# Creates a file path for the log file.
now = datetime.datetime.now()
path = log_folder(log_folder_path)
#path = r'C:\Users\Taylor\Desktop\Macro Logs\V3.0'
log_file_name = now.strftime("%Y-%B-%d_%H.%M.%S")
filename = f'{path}\{log_file_name}.log'

# create logger
logger = logging.getLogger("My_app")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s - %(funcName)s: %(message)s', datefmt='%H:%M:%S') 

file_handler = logging.FileHandler(filename)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()

stream_handler.setFormatter(CustomFormatter())
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# timer function

# from functools import wraps
# from time import perf_counter
# def get_time(func):
#     """Times any function\n
#     Use as decorator to time funcs\n
#     @get_time """

#     @wraps(func)
#     def timer(*args, **kwargs):
#         start_time = perf_counter()
        
#         func(*args, **kwargs)

#         end_time = perf_counter()
#         total_time = round(end_time - start_time, 6)

#         func_name = func.__name__
#         logger.info(f'{func_name} took {total_time} seconds to complete')
    
#     return timer


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


# def get_processes(sort = False):
#     """Returns list of dictionarys of all apps, their PIDS and hwnd\n
#     leave empty if you want the whole list
#     Put True in if you want the list sorted by title
#     """

#     @WNDENUMPROC
#     def py_callback( hwnd, lparam ):
#         pid = wintypes.DWORD()
#         tid = GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
#         if IsWindow(hwnd):
#             length = GetWindowTextLength(hwnd)
#             buff = ctypes.create_unicode_buffer(length + 1)
#             GetWindowText(hwnd, buff, length + 1) 

#             if buff.value and buff.value not in ['Default IME', 'MSCTFIME UI']:
#                 results.append({"Title": buff.value,
#                                 "PID": tid,
#                                 "HWND": hwnd})
#         return True

#     results = []
#     EnumWindows(py_callback,0)

#     if sort:
#         logger.debug("sorting")
#         resultslist = sorted(results, key=lambda d: d['Title'])
#         return resultslist

#     return results


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
    
    custom_keyboard.hotkey('winleft', 'shift', 's')
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
                    if event.pressed == False:
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

def ButtonMode(mode):
    ButtonDescriptions = f"""Current mode is: {mode}
    If button is not their nothing is assigned to it.
        
    Default/Mode 1/Works on any mode and unspecified app:
        Button 1:   Shows this
        Button 2:   Controls spotify: Acts like headphone controls.
        Button 3:   Switches desktop to the left
        Button 4:   Switches desktop to the right
        Button 5:   Text to speech, Converts highlighted text to speech
        Button 7:   Copy
        Button 8:   Paste
        Button 9:   
        Button 10:  Opens Task Manager
        Button 11:  Converts screenshot of text to text

    When in Vscode:
        Button 5:   run code in Vs code

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

SPEECH_KEY ='8819099d546f4a168f0b84e6abd78540'
SPEECH_REGION = 'westus'
# This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
# The language of the voice that speaks.
speech_config.speech_synthesis_voice_name='en-US-JennyNeural'
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

def textToSpeech():
    logger.info("in textToSpeech")
    pyautogui.hotkey('ctrl', 'c')
    text = pyperclip.paste()

    speech_synthesis_result = speech_synthesizer.speak_text_async(text)

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
    speech_synthesizer.stop_speaking_async()


def spotifyV3(timeout = 0.4, count=[0]):
    """Plays/Pauses spotifyV3, presses next song previous song.   
    
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
    
    logger.debug("Spotify Func Has been called")

    def spotify_timerV3():
        """Waits for timeout to finish then it send a keyboard input based on value of count[0]"""

        logger.debug("spotify_timer Has just begun")
        time.sleep(timeout)
        logger.debug("spotify_timer sleep has just finished")

        actions = [
            "playpause",
            "nexttrack",
            "prevtrack"]
        
        logger.debug("Entering try")
        try:
            action = actions[count[0]-1]
        
            custom_keyboard.press(action)  
            logger.debug(f'Value of {count[0] = }, executing folowing action: {action}')

        except IndexError as ind:
            print('\n')
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
        if spotify_timerV3.__name__ in thread.name
        ]
    
    if not any(thread_running):
        logger.debug("Thread I want is not running, starting it")
        spotify_thread = threading.Thread(target=spotify_timerV3, args=(),daemon=True)
        spotify_thread.start()
    else:
        logger.debug("thread I want is running")


# Gets the path of icon image
icon_path = fr"{script_path}\pythonIcon.ico"
image = Image.open(icon_path)    # Opens the Icon 
#https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread-in-python

toaster = ToastNotifier()
NOTIFICATION = {
    "ShowNotification": True,
    "Duration": 1.5
    }



def Button_handler(button):

    def sheild_focus_star_citizen(key): #macro to focus ship shields in star citizen
        logger.debug(f"right shift + {key}")
        custom_keyboard.hotkey('shiftright', key)
        time.sleep(0.1)
        custom_keyboard.press('shiftright')

    def change_desktop(direction, focused_app): #change desktop hotkey, where direction is either 'left' or 'right'. Will alt+tab if specific program is focused
        logger.debug(f"move desktop {direction}")
        
        apps_to_alt_tab = ['Star Citizen', 'Task Manager']  #lis of apps to alt tab when changing desktops

        if focused_app in apps_to_alt_tab: 
            custom_keyboard.hotkey('alt', 'tab')
            time.sleep(0.1)

        custom_keyboard.hotkey('ctrl', 'win', direction)

    focused_win_name = win32gui.GetWindowText(win32gui.GetForegroundWindow())

    win_name = focused_win_name.split(" - ")
    win_name.reverse()

    app = win_name[0]
    if app == '': #Sets app to 'Desktop' if nothing is focused.
        app = 'Desktop'

    #logger.debug(f"Focused app is {app}")

    # Match case for buttons.
    match [app, button.split()]:
        #Format: 
        #case [AppName, ("ButtonNumber", "MacroMode")]:
        # Leave AppName _ for any app
        # MacroMode as mode for any mode
    
        # Any app and Any Mode    And that are prioritives 
        case [_, ("1", mode)]:    # Shows what each button is defined as
            logger.debug("ButtonMode")
            twrv = threading.Thread(target = ButtonMode, args=(mode, )).start()

        case [_, ("2", mode)]:    # pause song spotify for any app
            logger.debug("pause song spotify \n")
            spotifyV3()

        case [_, ("3", mode)]:    # move desktop left for any app
            twrv = threading.Thread(target = change_desktop, args=('left', app)).start()

        case [_, ("4", mode)]:     # move desktop right for any app   
            twrv = threading.Thread(target = change_desktop, args=('right', app)).start()


        # Specific app but any Mode
        # VS Code Layer
        case ["Visual Studio Code", ("5", mode)]: # run code in Vs code
            logger.debug("run code in Vs code")
            pyautogui.hotkey('ctrl', 'alt', 'n') 

        # Star Citizen Layer
        case ["Star Citizen", ("5", mode)]: # focus front shields
            sheild_focus_star_citizen("1")

        case ["Star Citizen", ("6", mode)]: # focus back shields
            sheild_focus_star_citizen("2")

        case ["Star Citizen", ("7", mode)]: # Reset shields
            sheild_focus_star_citizen("3")
        

        # TEST
        case ["Destiny 2", ("5", mode)]: # Rocket Flying Test
            #left clicks, then presses q, then moves mouse down 15 pixels
            logger.debug("Rocket Flying Test")
            autoit.mouse_click()

            custom_keyboard.press('q')

            x,y = autoit.mouse_get_pos()

            autoit.mouse_move(x,y+15)
    
            logger.debug("wut")



        # Any App, Specific Mode
        case [_, ("5", "2")]:     # Cut (Ctrl + x)
            logger.debug("Audacity Cut (Ctrl + x)")
            custom_keyboard.hotkey('ctrl', 'x')
       
        case [_, ("6", "2")]:     # Audacity Split Ctrl + i 
            logger.debug("Audacity Split (ctrl + i)")
            custom_keyboard.hotkey('ctrl', 'i')

        case [_, ("9", "2")]:     # Backspace
            logger.debug("Backspace")
            custom_keyboard.press('backspace')

        # Macros that are last priority.     
        case [_, ("5", mode)]:   # Text to speech
            logger.debug("Text to speech")
            custom_keyboard.hotkey('ctrl', 'c')
            twrv = threading.Thread(target = textToSpeech, args=()).start()
        
        case [_, ("6", mode)]:   # Stop Speech
            logger.debug("Stop Speech")
            twrv = threading.Thread(target = stopSpeech, args=()).start()
        
        case [_, ("7", mode)]:   # Copy
            logger.debug("Copy")
            #NOTE : this can cause a keyboard interupt if used in terminal
            custom_keyboard.hotkey('ctrl', 'c')

        case [_, ("8", mode)]:   # Paste 
            logger.debug("Paste")
            custom_keyboard.hotkey('ctrl', 'v')

        case [_, ("0", mode)]:     # runs Task Manager      is button 10
            logger.debug("Starting Task manager")
            custom_keyboard.hotkey('ctrl', 'shift', 'esc')
                
        case [_, ("A", mode)]:   #image to text             is button 11
            logger.debug("Image to text")
            twrv = threading.Thread(target = Image_to_text2).start()

def on_quit(type):
    """
    Quits the program,
    ser.close() raises a index out of range error, 2 NoneType errors 
    then finally a serial.serialutil.PortNotOpenError execption
    which we catch in the main try. once we catch it wan can do sys.exit(1) 
    """
    logger.critical("PROGRAM is shutting down")
    systray.stop()
    if type == 1:
        ser.close()
    exit(1)
    #ser.close()

def setupV2(type=None):
    while True:
        if type is not None: # this used when trying to reconect to arduino
            time.sleep(type)

        try:
            """
            Tries to connect to the arduino.  Outputs None if it cant connect.
            """
            logger.info("Connecting to Arduino...")

            logger.info("Getting port")
            ports = serial.tools.list_ports.comports()
            logger.debug(f"{ports=}")

            # gets the port the arduino is connected to, returns [ ], if there is no arduino port
            arduinoPort = [port for port, desc, hwid in sorted(ports) if "Arduino Micro" in desc]
            logger.info("Got arduino port"), logger.debug(f"{arduinoPort=}")
            global ser
            ser = serial.Serial(arduinoPort[0], 9600)

        except serial.serialutil.SerialException as err:
            logger.error("Arduino is already connected to something, Access is denied.")
            
            if NOTIFICATION["ShowNotification"]:
                toaster.show_toast("Access is denied","Arduino is already connected to something", icon_path=None, duration=NOTIFICATION["Duration"], threaded=True)

            on_quit(0)

        except Exception as e:
        
            logger.error(e)
            time.sleep(0.2)
        else:
            logger.info("Connected to Arduino")

            if NOTIFICATION["ShowNotification"]:
                toaster.show_toast("Macro Keypad is connected", icon_path=None, duration=NOTIFICATION["Duration"], threaded=True)

            logger.info("Setup was a success")
            print()

            return ser

def sysIcon():
    global systray
    systray = pystray.Icon(name="Python Macro", icon=image, title="Python Macro", menu=pystray.Menu(
        #pystray.MenuItem("Quit", on_quit)
        pystray.MenuItem("Quit", lambda: on_quit(1))
    ))
    systray.run()


def main():
    # Makes the systray Icon a seperate thread so it doesn't block code
    twrv = threading.Thread(target = sysIcon).start()
    
    ## setup
    global ser
    ser = setupV2()
    
    while True:
        try: 
            cc = str(ser.readline())
            if 'mode button was pressed' in cc:
                logger.info(cc)
                continue

            #global button
            button = (f"{cc[9]} {cc[11]}")

            Button_handler(button)

        except serial.serialutil.PortNotOpenError:
            logger.critical("Arduino is not plugged in")
            logger.critical("Program quiting, goodbye")
            sys.exit(1) 

        except Exception as e:
            logger.warning(e)
            print()
            time.sleep(0.2)

            if type(e) is serial.SerialException:
                logger.warning("Arduino disconected, trying to reconect")
                toaster.show_toast("Arduino has been disconected", "Rrying to reconnect", icon_path=None, duration=3, threaded=True)
                print()
                ser = None
                setupV2(3)
                
if __name__ == "__main__":
    """
    Changelog:
        Updated spotify func, it is much smaller and doesnt need to get hwnd of spotify
        
        added 2 new functions, both are for getting app stats, like name and hwnd and pid
        they are currently commented out. 
        The Ctype stuff that is commented out just below imports is needed for the 2 functions to work
        I want to add them to another file called tools or utils or something, IDK

        changed image to text so that it pressed win shift s to open snippet mode.
        then it waits for you to release the left mouse then it grabs the image from clipboard
        and uses pytesseract to do OCR on it.

        added a func that checks and creates a log folders if there is not one.

        removed the need for the following modules: pywinauto, win32process, psutil

    TODO for V3.1:
        When I right click on the taskbar icon, I want there to be a toggle button
        When On I want it to open a console window that will print the debug and error messages to it
        and when off it goes away.

        try and transition all pyautogui keyboard funtions to custom_keyboard
        add a write function to custom_keyboard


    """

    main()
    
