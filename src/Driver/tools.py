import contextlib
from functools import wraps
from logger import logger, toaster
import custom_keyboard
import time
import pyperclip
import azure.cognitiveservices.speech as speechsdk
from PIL import ImageGrab
import pytesseract
import pyautogui
from pynput import mouse, keyboard
import autoit   ##### TO isntall it uses pip install pyautoit
import pywinauto
import psutil
import os
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

def get_processes(filter=['Default IME', 'MSCTFIME UI'], sortby='Title')-> list[dict]:
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

def get_focused():
    hwnd = win32gui.GetForegroundWindow()
    return win32gui.GetWindowText(hwnd), hwnd

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

def launchApp(name_or_path:str, timeout:int = 0.5) -> None:
    #logger.debug(name_or_path,timeout)
    try:
        os.startfile(name_or_path)
    except Exception as e:
        logger.warning(e)
    time.sleep(timeout)


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

def set_focus_to_desktop():
    processes = get_processes()
    for process in processes:
        if process['Title'] == 'Program Manager':
            win32gui.SetForegroundWindow(process['HWND'])
            return 0
    return 1

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
        
        set_focus_to_desktop()
        
        GoToDesktop(newDesktopNum)
    
    else:
        apps_to_alt_tab = ['Star Citizen']  #lis of apps to alt tab when changing desktops

        if focused_app in apps_to_alt_tab: 
            perform_hotkey(['alt', 'tab'])
            #custom_keyboard.hotkey('alt', 'tab')
            time.sleep(0.1)

        perform_hotkey(['ctrl', 'win', direction])
  
def moveAppAccrossDesktops(hwnd: int, movement: str) -> int:
    """Moves an app accross desktops.
    This function requires the VirtualDesktopAccessor.dll, if it is not installed, the  func will return 1
    If you input an app name, it will try and get the hwnd
    if the app is not active, the hwnd will be None and the func will return 0
    
    Movements are:
    'Left': Goes left,
    'Right': Goes Right,
    'Current': Moves to the current desktop
    
    Args:
        hwnd (HWND): The HWND(handle) of the app
        movement (str): Movement Type

    Returns:
        bool: It will return 1 if succesfull and 0 if not
    """
    if not VDA:
        msg = r"""VirtualDesktopAccessor.dll Cannot be found. This function will not work without it
        You can find it here: https://github.com/Ciantic/VirtualDesktopAccessor?tab=readme-ov-file, make sure you download the correct version for your operating system. \nPut it in "C:\Windows\System32" """
        logger.warning(msg)
        return 1
    #logger.debug(hwnd)
    
    if hwnd is None:
        logger.debug("hwnd is None")
        #launchApp(hwnd)
        return 0
    
    movements = {
        'Left': (GetWindowDesktopNumber(hwnd) -1),
        'Right': (GetWindowDesktopNumber(hwnd) +1),
        'Current': CurrentDesktopNumber()
        }

    destination = movements[movement]
    return MoveAppToDesktop(hwnd, destination) 

class MediaTimer:
    """
    This will sometimes return None
    """
    def __init__(self):
        self.timer_active = False
        self.count = 0
        
        self.ACTIONS = [
            "PlayPause",
            "NextTrack",
            "PrevTrack"]

    def start_timer(self, duration):
        self.timer_active = True
        time.sleep(duration)
        self.timer_active = False
        return self.handle_action()

    def handle_action(self):
        try:
        
            action = self.ACTIONS[self.count-1]
            self.count = 0  # Reset count after handling action
            return action
        except IndexError:
            logger.warning(f'Button was pressed to many times. You pressed it {self.count} times.\n')
            self.count = 0

    def press_button(self):
        self.count += 1     
        
        if not self.timer_active:
            return self.start_timer(0.55)
    
class SpotifyController:
    """A Controller Class for Spotify
    """
    def __init__(self):
        self.SPOTIFY_HOTKEYS = {
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
        
        self.mediaTimer = MediaTimer()
        self.spotify_app = None
        
        self.spotify_HWND = None
        #self.spotify_app = self._connect()
               
    def _app_connect(self):
        if PID := pidGetter('Spotify'):
            app = pywinauto.application.Application().connect(process=PID, timeout=2)
        else:
            logger.debug("Couldn't find spotify")
            launchApp('Spotify')
            time.sleep(0.75)
            app = pywinauto.application.Application().connect(process=pidGetter('Spotify'), timeout=2)
        app = app["Chrome_Widget_Win0"]
        
        return app
        
    def _get_spotify_HWND(self):
        # Put into its own function, where a param is a key you want to filter by
        processes = get_processes()
        sorted_processes_by_Pid= sorted(processes, key=lambda x: x['PID'])
        
        for index, process in enumerate(sorted_processes_by_Pid):
            
            if 'GDI+ Window (Spotify.exe)' in process['Title']:
                PID = process['PID']
                process_above_in_the_list = sorted_processes_by_Pid[index - 1]
                
                if process_above_in_the_list['PID'] == PID:
                    
                    spotify = process_above_in_the_list
                    
                    break
            
        print(spotify)   
         
        if not spotify:
            logger.debug("looks like spotify is not running.")
            
            self.launch_spotify()
            
        self.spotify_HWND = spotify['HWND']
            
    def launch_spotify(self):
        logger.debug("Launching Spotify")
        
        launchApp('Spotify')
        time.sleep(0.75)
        
        self.spotify_app = self._app_connect()
        
    def event_handler(self, event):
        if self.spotify_app is None:
            self.spotify_app = self._app_connect()
            
        try:
            self.spotify_app.send_keystrokes(self.SPOTIFY_HOTKEYS[event])
        
        except pywinauto.findbestmatch.MatchError:
            logger.warning("Spotify Timed out, will asume its not running.")
            self.launch_spotify()
            self.spotify_app.send_keystrokes(self.SPOTIFY_HOTKEYS[event])

    def press(self):
        if result := self.mediaTimer.press_button():
            logger.debug(result)
            self.event_handler(result)

    def move_spotify_window(self, direction):
        if not self.spotify_HWND:
            self._get_spotify_HWND()
            
        moveAppAccrossDesktops(self.spotify_HWND, direction)

class ChromeController:
    """A Controller Class for Chrome
    """
    def __init__(self):
        self.actions = {
                'PrevTrack': 'Previous Track',
                'SeekBackward': 'Seek Backward',
                'PlayPause': 'Play Pause',
                'SeekForward': 'Seek Forward',
                'NextTrack': 'Next Track'
                }
        
        self.mediaTimer = MediaTimer()
        self.Chrome_Parent_PID = None
        self.Chrome_app = None
 
        
    def _app_connect(self):
        if self.Chrome_Parent_PID is None:
            #logger.debug("Chrome_Parent_PID is False")
            PID = pidGetter('chrome')
            if PID is None:
                logger.debug('There is no app with name of "chrome"')
                return
            self.Chrome_Parent_PID = PID
        
        app = pywinauto.application.Application(backend="uia").connect(process=self.Chrome_Parent_PID)
        return app
    
    def event_handler(self, event):
        if self.Chrome_app is None:
            print("in self.Chrome_app is None")
            self.Chrome_app = self._app_connect()
        
        logger.debug("Connected to Chrome")

        media_control_button = self.Chrome_app.window().child_window(title="Control your music, videos, and more", control_type="Button")
        
        logger.debug("got media_control_button")
        try:
            media_control_button.click()
        except Exception as e:
            print(e)
            print("There is nothing in the Global Media Controls")
            return 

        #time.sleep(0.1)

        ### this skips right to it
        last_video_media_control = self.Chrome_app.window().child_window(title="Back to tab", control_type="Button", found_index=0)
        media_controls = last_video_media_control.children()
        
        
        action_todo =  self.actions[event]
        for index, controls in enumerate(media_controls):
            if controls.window_text() in action_todo:
                #logger.debug("I found the button")
                media_controls[index].click()
                break
        logger.debug(f"pressed media_controls { self.actions[event]}")

        media_control_button.click()
        

    def press(self):
        if result := self.mediaTimer.press_button():
            logger.debug(result)
            self.event_handler(result)

class YTMusicController:
    """A Controller Class for Youtube Music app on windows 10
    """
    def __init__(self):
        self.YTMUSIC_HOTKEYS = {
                "VolumeUp": "=",
                "VolumeDown": "-",
                "PrevTrack": "k",
                "NextTrack": "j",
                "PlayPause": ";",#"{SPACE}"
                "Back5s": "+{LEFT}",
                "Forward5s": "+{RIGHT}",
            }
                
        self.mediaTimer = MediaTimer()
        # self.ytmusic_app = None
        # self.is_playing_music = False
        # self.ytmusic_PID = None
        
    def launch_ytmusic(self):
        #logger.debug("Launching Spotify")
        
        launchApp(r'C:\Users\Taylor\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Chrome Apps\YouTube Music')
        time.sleep(0.75)

    def get_app_info(self, app_name: str) -> list:
        """Returns a list of information of an specified app.
        """
        processes = get_processes()
        for process in processes:
            if app_name in process['Title']:
                return process

    
    def event_handler(self, event):
        #ytmusic = get_app_info('YouTube Music')
    
        if ytmusic_info := self.get_app_info('YouTube Music'):
            try:
                app = pywinauto.application.Application().connect(process=ytmusic_info['PID'], timeout=2)
            
                yt_music_app = app.window(title=ytmusic_info['Title'])
                
                yt_music_app.send_keystrokes(self.YTMUSIC_HOTKEYS[event])
        

            except pywinauto.findbestmatch.MatchError:
                #logger.warning("ytmusic Timed out, will asume its not running.")
                self.launch_ytmusic()

        else:
            self.launch_ytmusic()
            
    def press(self):
        if result := self.mediaTimer.press_button():
            #logger.debug(result)
            print(result)
            self.event_handler(result)