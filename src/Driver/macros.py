"""
All the stuff from tools.py will be moved here
"""

from setup import logger, send_notification
from functools import wraps
import time
import sys
import os
import azure.cognitiveservices.speech as speechsdk
import pyperclip
import pyautogui

logger.debug(f'Initializing {__file__}')

# if sys.platform == 'win32':
#     from _windows_macros import SpotifyController
#     from _windows_macros import ChromeController
#     from _windows_macros import YTMusicController
#     from _windows_macros import change_desktop
#     from _windows_macros import perform_hotkey
#     from _windows_macros import perform_press
    
#     #perform_hotkey
# elif sys.platform == 'linux':
#     from _linux_macros import SpotifyController
#     from _linux_macros import ChromeController
#     from _linux_macros import YTMusicController
#     from _linux_macros import change_desktop
#     from _linux_macros import perform_hotkey
#     from _linux_macros import perform_press


if sys.platform == 'win32':
    # make this a class
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

#############################################     General Macros     #############################################
"""
These should work on both systems
"""

def libreOffice_zoomin():   
    pyautogui.keyDown('ctrl')
    pyautogui.hscroll(10)
    pyautogui.keyUp('ctrl')

def libreOffice_zoomout():
    pyautogui.keyDown('ctrl')
    pyautogui.hscroll(-10)
    pyautogui.keyUp('ctrl')

def sheild_focus_star_citizen(key): #macro to focus ship shields in star citizen
    logger.debug(f"right shift + {key}")
    # custom_keyboard.hotkey('shiftright', key)
    # time.sleep(0.1)
    # custom_keyboard.press('shiftright')

    perform_hotkey(['shiftright', key])
    time.sleep(0.1)
    perform_press('shiftright')
    
def wellskate(): #wellskate
    """ Performs the wellskate macro for destiny 2"""
    logger.debug("Wellskate")
    perform_press('3')
    time.sleep(0.5)
    pyautogui.click(button='right')
    perform_hotkey(['space', 'f'])
    time.sleep(0.1)
    perform_press('1')
    
def search_highlighted_text():
    """Searches highlighted text in google Chrome. Should work for other browsers.

    Copies highlighted text, opens new tab, pastes text, presses enter.
    This works on Windows, should work on linux
    """
    logger.debug("in search_highlighted_text")
    perform_hotkey(['ctrl', 'c'])

    time.sleep(0.1)

    perform_hotkey(['ctrl', 't'])
    time.sleep(0.2)

    perform_hotkey(['ctrl', 'v'])
    time.sleep(0.2)
    
    perform_press('enter')
    
#############################################     OS specific Macros     #############################################

if sys.platform == 'win32':
    import _windows_macros as platformModule
elif sys.platform == 'linux':
    import _linux_macros as platformModule

# class SpotifyController:
#     # https://stackoverflow.com/questions/70737550/how-to-connect-to-mediaplayer2-player-playbackstatus-signal-using-pygtk
#     # https://www.reddit.com/r/linuxquestions/comments/mv9z12/how_does_linux_handle_playpause_from_function_keys/
#     def __init__(self):
#         platformModule._SpotifyController
       
# class ChromeController:
#     """A Controller Class for Chrome  IT is currently broken
#     """
#     def __init__(self):
#         platformModule._ChromeController
   
# class YTMusicController:
#     """A Controller Class for Youtube Music app, I might be able to use the same methoda as the spotify controller, but not right now.
#     I navent event used YT music after setting up the controller.
#     """
#     def __init__(self):
#         platformModule._YTMusicController

def SpotifyController():
    # https://stackoverflow.com/questions/70737550/how-to-connect-to-mediaplayer2-player-playbackstatus-signal-using-pygtk
    # https://www.reddit.com/r/linuxquestions/comments/mv9z12/how_does_linux_handle_playpause_from_function_keys/
 
    return platformModule._SpotifyController()
       
def ChromeController():
    """A Controller Class for Chrome  IT is currently broken
    """
    return platformModule._ChromeController()
   
def YTMusicController():
    """A Controller Class for Youtube Music app, I might be able to use the same methoda as the spotify controller, but not right now.
    I navent event used YT music after setting up the controller.
    """
    return platformModule._YTMusicController()


def perform_hotkey(hotkey):
    logger.debug(f"perform_hotkey {hotkey = }")
    platformModule._perform_hotkey(hotkey)

def perform_press(key):
    logger.debug(f"perform_press {key = }")
    platformModule._perform_press(key)

#def change_desktop(direction:str, focused_app=None): #change desktop hotkey, where direction is either 'left' or 'right'. Will alt+tab if specific program is focused
def change_desktop(direction, focused_app): #change desktop hotkey, where direction is either 'left' or 'right'. Will alt+tab if specific program is focused
    """Changes the desktop, moves left or right

    Args:
        direction (str): Either: 'left' or 'right'
        focused_app (str): Does nothing, its here to allow compatibility with the windows version
    """
    logger.debug(f"move desktop {direction}")
    
    platformModule._change_desktop(direction, focused_app)

def moveAppAccrossDesktops(app_id: int, move: str):
    """Moves an app accross desktops.
    This function requires the VirtualDesktopAccessor.dll on windows,
    It is not implemented yet on linux
    
    Movements are:
    'Left': Goes left,
    'Right': Goes Right,
    'Current': Moves to the current desktop
    
    Args:
        app_id (HWND|window_id): The HWND(handle) of the app
        movement (str): Movement Type

    Returns:
        bool: It will return 1 if succesfull and 0 if not
    """
    #return platformModule._moveAppAccrossDesktops(hwnd, movement)
    return platformModule._moveAppAccrossDesktops(app_id=app_id, movement= move)

def Image_to_text2():
    """Presses Win Shift S to open snippet mode, waits for mouse release then does tesseract OCR
    Press Ctrl V to paste text
    """
    logger.debug("Image_to_text2 has just started")
    platformModule._Image_to_text2()
    logger.debug("Image_to_text2 has finished")


def get_focused():
    
    return platformModule._get_focused()
def get_focused_name():
    
    return platformModule._get_focused_name()


# import SpotifyController
# import ChromeController
# import YTMusicController
# import change_desktop
# import perform_press
# import perform_hotkey
logger.debug(f"Initializing is complete for {__file__}")