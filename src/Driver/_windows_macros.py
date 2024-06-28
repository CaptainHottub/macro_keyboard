"""
All the windows specific stuff will be moved here
"""
import contextlib
from setup import logger
import time
import pywinauto
import psutil
import os
import ctypes
import custom_keyboard

import pyperclip
from PIL import ImageGrab
import pytesseract
from pynput import mouse, keyboard
import win32gui
import win32process


logger.debug(f'Initializing {__file__}')

VDA = False


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
    logger.warning(e)
    VDA = False
else:
    VDA = True
#logger.debug(VDA)

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

def _get_focused():
    hwnd = win32gui.GetForegroundWindow()
    return win32gui.GetWindowText(hwnd), hwnd

def _get_focused_name():
    return _get_focused()

def get_forground_hwnd():
    processes = get_processes()
    for process in processes:
        if process['Title'] == 'Program Manager':
            return process['HWND']
    
    return None
    
def launchApp(name_or_path:str, timeout:int = 0.5):
    #logger.debug(name_or_path,timeout)
    try:
        os.startfile(name_or_path)
    except Exception as e:
        logger.warning(e)
    time.sleep(timeout)


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


#############################################     Macros that can be called     #############################################
class _SpotifyController:
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
        processes = get_processes(sortby='PID')
        
        for index, process in enumerate(processes):
            
            if 'GDI+ Window (Spotify.exe)' in process['Title']:
                PID = process['PID']
                process_above_in_the_list = processes[index - 1]
                
                if process_above_in_the_list['PID'] == PID and process_above_in_the_list['Title'] == 'Spotify Premium':
                    
                    spotify = process_above_in_the_list
                    
                    break
            
        #print(spotify)   
         
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
            
        _moveAppAccrossDesktops(self.spotify_HWND, direction)

class _ChromeController:
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

class _YTMusicController:
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

def _perform_hotkey(hotkey):
    #logger.debug(f"perform_hotkey {hotkey = }")
    custom_keyboard.hotkey(*hotkey)

def _perform_press(key):
    #logger.debug(f"perform_press {key = }")
    custom_keyboard.press(key)

#def _moveAppAccrossDesktops(hwnd: int, movement: str):
def _moveAppAccrossDesktops(**kwargs):
    """Moves an app accross desktops.
    This function requires the VirtualDesktopAccessor.dll, if it is not installed, the  func will return 1
    if app_id is blank, it will move the focused one

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
    if VDA:
        #logger.debug(hwnd)
        
        if 'hwnd' in kwargs:
            hwnd = kwargs['hwnd']
        else:
            hwnd = _get_focused()
            
        if 'movement' in kwargs:
            movement = kwargs['movement'].lower()
        else:
            movement = 'current'
            
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
    
    else:
        msg = r"""VirtualDesktopAccessor.dll Cannot be found. This function will not work without it
        You can find it here: https://github.com/Ciantic/VirtualDesktopAccessor?tab=readme-ov-file, make sure you download the correct version for your operating system. \nPut it in "C:\Windows\System32" """
        logger.warning(msg)
        return 1

def _change_desktop(direction, focused_app): #change desktop hotkey, where direction is either 'left' or 'right'. Will alt+tab if specific program is focused
    """
    The VDA one take on average 5 ms to complete, IT also doesn't need to alt tab some apps like task manager
    while the other one takes 100 ms to complete
    """
    logger.debug(f"move desktop {direction}")
    if VDA:
        #### this is so much faster!!!!
        try: 
            global forground_hwnd
            win32gui.SetForegroundWindow(forground_hwnd)
        except Exception as e:
            print(e)
            if isinstance(e, win32gui.error):
                #It's not actually a win32gui error, its from pywintypes.error, and win32gui imports it as error.
                forground_hwnd = get_forground_hwnd()

        if direction == 'left':
            newDesktopNum = CurrentDesktopNumber() -1
        elif direction == 'right':
            newDesktopNum = CurrentDesktopNumber() + 1
    
        GoToDesktop(newDesktopNum)
    
    else:

        apps_to_alt_tab = ['Star Citizen']  #lis of apps to alt tab when changing desktops

        if focused_app in apps_to_alt_tab: 
            _perform_hotkey(['alt', 'tab'])
            #custom_keyboard.hotkey('alt', 'tab')
            time.sleep(0.1)
    
        _perform_hotkey(['ctrl', 'win', direction])

def _Image_to_text2():
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
    
    _perform_hotkey(['winleft', 'shift', 's'])
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

def _start_task_viwer():
    """Opens Task Manager"""
    _perform_hotkey(['ctrl', 'shift', 'esc'])

logger.debug(f"Initializing is complete for {__file__}")