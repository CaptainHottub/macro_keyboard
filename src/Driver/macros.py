"""
All the stuff from tools.py will be moved here
"""

from setup import logger, send_notification
from functools import wraps
import time
import sys
import os
import azure.cognitiveservices.speech as speechsdk
import pyautogui
import pyclip       # import pyperclip   
import sounddevice as sd
import soundfile as sf
import threading

logger.debug(f'Initializing {__file__}')

try:
    """
    OMFG, it only works with azure-cognitiveservices-speech==1.37.0
    and openssl 1.1
    # https://github.com/Azure-Samples/cognitive-services-speech-sdk/issues/2436

    For the lifee of me i cant get this to work on linux. There was this whole megathread on github about the openssl 1.x EOL: https://github.com/Azure-Samples/cognitive-services-speech-sdk/issues/2048
    """
    if speechsdk.__version__ != '1.37.0':
        raise ModuleNotFoundError("You are using the wrong version of azure-cognitiveservices-speech. You must use version 1.37.0")
    
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

##WTF this wont work in the konsole profile launcher
def textToSpeech():
    logger.info("in textToSpeech")
    """Microsoft Azure moves to TLS 1.2 On October 31 2024
    IDK what that really means, so if this breaks after that date, we will know why
    https://learn.microsoft.com/en-us/security/engineering/solving-tls1-problem
    """
    #perform_hotkey(['ctrl', 'c'])
    pyautogui.hotkey(['ctrl', 'c'])
    time.sleep(0.1)
    text = pyclip.paste(text=True)
    speech_synthesizer.speak_text_async(text)
    logger.info("textToSpeech has finished")
    #speech_synthesizer.speak_text(text)
    #speech_synthesis_result = speech_synthesizer.speak_text_async(text)

def stopSpeech():
    logger.info("in stopSpeech")
    #speech_synthesizer.stop_speaking()
    speech_synthesizer.stop_speaking_async()

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

def ButtonMode(mode):
    """Prints to the terminal, i havent updated what is says, so it might be wrong."""
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
    print('\n\n')
    logger.info(ButtonDescriptions)
    print('\n\n')
    
    # try:
    #     pyautogui.alert(ButtonDescriptions, "Button Mode")  
    # except Exception as e:
    #     logger.warning(e)

def libreOffice_zoomin():   
    pyautogui.keyDown('ctrl', _pause=False)
    pyautogui.hscroll(1, _pause=False)
    pyautogui.keyUp('ctrl', _pause=False)

def libreOffice_zoomout():
    pyautogui.keyDown('ctrl', _pause=False)
    pyautogui.hscroll(-1, _pause=False)
    pyautogui.keyUp('ctrl', _pause=False)
    
def libreOffice_font_size_up():   
    pyautogui.hotkey('ctrl', ']', _pause=False)

def libreOffice_font_size_down():
    pyautogui.hotkey('ctrl', '[', _pause=False)


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


def play_audio_on_devices(filename, devices=["default"], volume=0.5):
    """Basically a soundboard.          

    To list devices: print(sd.query_devices())  

    # Example usage:        
    devices = ["default", "HELLDIVERS"]     
    play_audio_on_devices(test.mp3, devices, volume=0.5)       
    play_audio_on_devices(AHHHHH.mp3, volume=0.5)        

    Args:
        filename (str): Audio file you want to play
        devices (list, optional): The audio device you want the audio outputed to. Defaults to "default".
        volume (float, optional): Float val from 1.0 to 0. Defaults to 0.5.
    """
    full_path = os.path.abspath(os.path.expanduser(filename))
    
    def play_on_device(filename, device, volume):
        with sf.SoundFile(filename) as f:
            with sd.OutputStream(channels=f.channels, device=device) as stream:
                blocksize = 1024
                while True:
                    data = f.read(blocksize, dtype='float32')
                    data *= volume
                    if len(data) == 0:
                        break
                    stream.write(data)

    threads = []
    for device in devices:
        t = threading.Thread(target=play_on_device, args=(full_path, device, volume), daemon=True)
        t.start()
        threads.append(t)
    # Optional: wait for all threads to finish
    for t in threads:
        t.join()
        
    logger.debug("Succesfully Finished play_audio_on_devices")

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
    """A Controller Class for Youtube Music app, I might be able to use the same method as the spotify controller, but not right now.
    I havent event used YT music after setting up the controller.
    """
    return platformModule._YTMusicController()

def FireFoxController():
    """A Controller Class for FireFox. This is a very early test""" 
    return platformModule._FireFoxController()


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

def start_task_viwer():
    platformModule._start_task_viwer()
    #("Starting Task manager")

def get_focused_window_info():
    """
    Returns the Name and the HWND of the focused window.
    """
    return platformModule._get_focused_window_info()
    

logger.debug(f"Initializing is complete for {__file__}")