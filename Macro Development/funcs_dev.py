import contextlib
import threading
from threading import Thread
import warnings
import psutil
import pyautogui
import os, win32gui, win32process
import pyperclip
from pywinauto import Application
from ctypes import windll
from PIL import ImageGrab
import logging
import time
#from tqdm import tqdm

import azure.cognitiveservices.speech as speechsdk


user32 = windll.user32
user32.SetProcessDPIAware() # optional, makes functions return real pixel numbers instead of scaled values
full_screen_rect = (0, 0, user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))

#Custom logger
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

def logger_setup(level):
    # create logger with 'spam_application'
    global log
    log = logging.getLogger("My_app")

    if level == 0:
        log.setLevel(logging.INFO)
    else:
        log.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    if level == 0:
        ch.setLevel(logging.INFO)
    else:
        ch.setLevel(logging.DEBUG)
        
    ch.setFormatter(CustomFormatter())
    log.addHandler(ch)

# log.debug("debug message")
# log.info("info message")
# log.warning("warning message")
# log.error("error message")
# log.critical("critical message")

### find PID of app, 
def findProcessIdByName(processName): # This returns the parent of the procces Name, 
    """
    Returns a list of all the process ID's with a specific name.
    
    Args:
        processName (str) - Name of the process you want to find.
        Ex: "Spotify"
        
    Returns:
        (listOfProcessIds) List of all process ID's with a specific name.

    NOTE: Function will not work if processName is empty

    try:
    for p in psutil.process_iter(['name']):
        if processName in p.info['name']:
            parent = p.parent()
            if parent != None:
                return parent.pid
            
    except Exception as e:
        log.error(f"Exception Raised: {e}")
        return None
    """
    listOfProcessIds = []
    for proc in psutil.process_iter():
        with contextlib.suppress(psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pinfo = proc.as_dict(attrs=['pid', 'name'])
            if processName.lower() in pinfo['name'].lower() :
                listOfProcessIds.append(pinfo['pid'])
    return listOfProcessIds

def is_fullscreen():
    try:
        hWnd = user32.GetForegroundWindow()
        rect = win32gui.GetWindowRect(hWnd)
        if 'Google Chrome' in win32gui.GetWindowText(hWnd): # if youtube or google chrome is in the name of the window.
            return False
        return rect == full_screen_rect
    except Exception:
        return False

def Change_desktop(direction): #change desktop hotkey, where direction is either 'left' or 'right'. Will alt+tab is program is in fullscreen mode
    # twrv = ThreadWithReturnValue(target=is_fullscreen, args=())
    # twrv.start()
    # full = twrv.join()
    # full = is_fullscreen()
    # if full == True:
    #     pyautogui.hotkey('alt', 'tab')  
    pyautogui.hotkey('ctrl', 'win', direction)      

def Image_to_text():
    img = ImageGrab.grabclipboard()
    img.save("C:/Users/Taylor/itt/image.png")
    os.system('cmd /c "cd C:\\Users\\Taylor\\itt & tesseract Image.png tesseract-result"')
    
    file = open("C:\\Users\\Taylor\\itt\\tesseract-result.txt", 'r', encoding='utf-8').read()
    # removes the arrow from the text
    if '\n\x0c' in file:
        file = file.replace('\n\x0c','')
    pyperclip.copy(file)

def input_special_char():
    promptText= """ What greek letter, operator or maths operation do you want
    Greek letters   Codes
    Theta                 theta
    lambda              lambda
    pi                          pi
    Delta                  Delta
    Ohm                   Omega

    Operators       Codes
    Multiply            times
    Divide              div
    Multiply Dot    cdot
    Infinity               infty

    Maths operation Codes:
    Fraction                     frac
    Sqrt                         sqrt
    Root                       rootof
    """

    # operator = pyautogui.prompt(text=promptText)
    # pyautogui.write(f"\{operator}")
    # pyautogui.press("space")


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

count =0
spotify_PID = None
def spotifyV2(timeout = 0.5):
    """Plays/Pauses spotifyV2, presses next song previous song.   
    
    Press 1 time in timeout seconds to Plays/Pauses.     
     Press 2 times in timeout seconds to get next song.  
    Press 3 times in timeout seconds to get previous song.   
     If Spotify is not running presses 2 and 3 will be ignored and play/pause will happen

    Args:
      timeout (integer): Defines how much time you have
       to press the button for it to do something
    Returns:
      None
    """
    log.debug("Spotify Func Has been called")

    thread_running = None
    global count
    count += 1
    
    def get_spotify_stats():
        log.debug("get_spotify_stats Has just started")
        
        try:
            log.debug("Getting Current focused PID")
            global current_focused_pid
            current_focused_pid = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())
            log.debug(f"Current Focused PID is: {current_focused_pid}")

            log.debug("Check If Spotify is running")
            for p in psutil.process_iter(['name']):
                if 'Spotify' in p.info['name'] and p.parent() != None:
                    log.debug("Spotify is running")

                    global spotify_PID
                    spotify_PID = p.parent().pid

                    log.debug(f"Spotify PID is: {spotify_PID}")
                    break
            else:
                log.debug("Spotify is not running")
                spotify_PID = None
                return
            
        except Exception as e:
            log.error(f"Exception Raised: {e}")


    def spotify_timerV2(timeout):
        log.debug("spotify_timer Has just begun")
        time.sleep(timeout)
        log.debug("spotify_timer sleep has just finished")

        global count

        # True is spotify is focused, and False if not
        spotify_focussed = spotify_PID in current_focused_pid

        if spotify_PID is None: #Spotify is not running
            log.debug("Spotify is not running")
            pyautogui.press("playpause")  
            return

        match [count, spotify_focussed]: #spotify is Running, 
            case [1, True]: #count is 1, and focused
                log.debug("spotify is Running, count is 1, and focused")
                pyautogui.press("playpause")  

            case [1, False]: #count is 1, and not focused
                log.debug("spotify is Running, count is 1, and not focused")
                app = Application().connect(process=spotify_PID)
                app.window().send_keystrokes(" ")

            case [2, _]: #count is 2, and any focused
                log.debug("#spotify is Running, count is 2, and any focused")
                log.debug("next song")
                pyautogui.press("nexttrack")
                
            case [3, _]: #count is 3, and any focused
                log.debug("spotify is Running, count is 3, and any focused")
                log.debug("previous song")
                pyautogui.press("prevtrack")

        
        log.debug(f"Value of Count is: {count}")
        count =0
        log.debug(f"Value of Count is now: {count}")
        print("\n")

    
    sp_tmrV2 = Thread(target=spotify_timerV2, args=(timeout,),daemon=True)
    sp_stat = Thread(target=get_spotify_stats, args=(),daemon=True)
    log.debug("sp_tmrV2 and sp_stat has been defined")

    log.debug("Check if thread is running")
    for thread in threading.enumerate():
        if '(spotify_timerV2)' in thread.name or '(get_spotify_stats)' in thread.name:
            log.debug("Spotify timer and or spotify stats thread are running")
            thread_running = True
            break
        else:
            log.debug("Thread I want is not running")
            thread_running = False

    log.debug("Just passed Check if thread is running")
    log.debug(f"thread_running value is: {thread_running}")

    if thread_running is False:
        log.debug("thread_running is False")
        log.debug("Starting: sp_tmr.start(), and sp_stat.start()")
        sp_tmrV2.start()
        sp_stat.start()

SPEECH_KEY ='6b2625a5e0cf43f09c888af1342080ea'
SPEECH_REGION = 'westus'
# This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
# The language of the voice that speaks.
speech_config.speech_synthesis_voice_name='en-US-JennyNeural'
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

def textToSpeech(before):

    log.info("in textToSpeech")
    raw_text = pyperclip.paste()
    if before == raw_text:
        log.debug("Texts are the same")
        log.debug(raw_text)
        log.debug(before)
        speech_synthesizer.stop_speaking()
    else:
        log.info("Texts are Not the same")
        cleaned_text = raw_text.replace("\r\n", " ")    

        good_text = cleaned_text.split(". ")
        print(good_text)

        for i in good_text:
            if len(i) > 1:
                speech_synthesis_result = speech_synthesizer.speak_text_async(i)