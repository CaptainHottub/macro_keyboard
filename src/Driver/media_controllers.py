from setup import logger

import time
import pywinauto
import psutil
import os
import sys


import ctypes
import subprocess
VDA = False
if sys.platform == 'win32':
    import win32gui
    import win32process

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

def _get_processes(filter=['Default IME', 'MSCTFIME UI'], sortby='Title')-> list[dict]:
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

def _get_focused():
    hwnd = win32gui.GetForegroundWindow()
    return win32gui.GetWindowText(hwnd), hwnd


def _pidGetter(name: str)-> int: 
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

def _launchApp(name_or_path:str, timeout:int = 0.5) -> None:
    #logger.debug(name_or_path,timeout)
    try:
        os.startfile(name_or_path)
    except Exception as e:
        logger.warning(e)
    time.sleep(timeout)

def _moveAppAccrossDesktops(hwnd: int, movement: str) -> int:
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
    if VDA and sys.platform == 'win32':
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
    
    else:
        msg = r"""VirtualDesktopAccessor.dll Cannot be found. This function will not work without it
        You can find it here: https://github.com/Ciantic/VirtualDesktopAccessor?tab=readme-ov-file, make sure you download the correct version for your operating system. \nPut it in "C:\Windows\System32" """
        logger.warning(msg)
        return 1
    
    
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


class _SpotifyController_win32:
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
        if PID := _pidGetter('Spotify'):
            app = pywinauto.application.Application().connect(process=PID, timeout=2)
        else:
            logger.debug("Couldn't find spotify")
            _launchApp('Spotify')
            time.sleep(0.75)
            app = pywinauto.application.Application().connect(process=_pidGetter('Spotify'), timeout=2)
        app = app["Chrome_Widget_Win0"]
        
        return app
        
    def _get_spotify_HWND(self):
        # Put into its own function, where a param is a key you want to filter by
        processes = _get_processes()
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
        
        _launchApp('Spotify')
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

class _ChromeController_win32:
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
            PID = _pidGetter('chrome')
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

class _YTMusicController_win32:
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
        
        _launchApp(r'C:\Users\Taylor\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Chrome Apps\YouTube Music')
        time.sleep(0.75)

    def get_app_info(self, app_name: str) -> list:
        """Returns a list of information of an specified app.
        """
        processes = _get_processes()
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


class _SpotifyController_linux:
    # https://stackoverflow.com/questions/70737550/how-to-connect-to-mediaplayer2-player-playbackstatus-signal-using-pygtk
    # https://www.reddit.com/r/linuxquestions/comments/mv9z12/how_does_linux_handle_playpause_from_function_keys/
    def __init__(self):
        self.main_msg = [
            'dbus-send', 
            '--print-reply', 
            '--session',
            '--dest=org.mpris.MediaPlayer2.spotify', 
            '/org/mpris/MediaPlayer2']
        self.event_translation_layer = {
            "PlayPause": "PlayPause", 
            "PrevTrack":"Previous", 
            "NextTrack":"Next"}
        
        self.mediaTimer = MediaTimer()

    def sendCommand(self, cmd):
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return proc.communicate()

    # use this: https://specifications.freedesktop.org/mpris-spec/latest/Player_Interface.html
    #https://github.com/DeaDBeeF-Player/deadbeef/issues/1785
    def event_handler(self, event):

        if event in ["PlayPause", "PrevTrack", "NextTrack"]:
            final_msg = self.main_msg + [f'org.mpris.MediaPlayer2.Player.{self.event_translation_layer[event]}']

        elif event in ['VolumeUp', 'VolumeDown']:
            #https://github.com/DeaDBeeF-Player/deadbeef/issues/1785
            get_volume_msg = self.main_msg+['org.freedesktop.DBus.Properties.Get', 
                                'string:org.mpris.MediaPlayer2.Player', 
                                'string:Volume']

            outputmsg = self.sendCommand(get_volume_msg)

            intermidiate = outputmsg[0].split("double ")
            volume = intermidiate[-1][0:-1]

            volume = float(volume)

            if event == 'VolumeUp':
                new_volume = volume + 0.05
            else:
                new_volume = volume - 0.05

            if new_volume > 1.0:
                logger.debug("vol is greater then 1")
                return

            get_volume_msg[5] = 'org.freedesktop.DBus.Properties.Set'
            get_volume_msg.append(f'variant:double:{new_volume:.2f}')
            final_msg = get_volume_msg
            
        
        elif event in ["Back5s", "Forward5s"]: # https://gitlab.gnome.org/World/podcasts/-/issues/238

            if event == "Forward5s":
                #seek is in microseconds
                seek_by = 5000000
            else:
                seek_by = -5000000
            final_msg = self.main_msg + ['org.mpris.MediaPlayer2.Player.Seek', f'int64:{seek_by}']

            #print(sendCommand(seek_msg))
        self.sendCommand(final_msg)

    def press(self):
        if result := self.mediaTimer.press_button():
            logger.debug(result)
            self.event_handler(result)
        
class _ChromeController_linux:
    """A Controller Class for Chrome  IT is currently broken
    """
    def __init__(self):
        logger.warning(""" pywinauto.application.Application().connect() doesn't seem to work for me, so this controller doesnt work
                       I'm going to fix it one day, but Idk when.""")
        self.actions = {
                'PrevTrack': 'Previous Track',
                'SeekBackward': 'Seek Backward',
                'PlayPause': 'Play Pause',
                'SeekForward': 'Seek Forward',
                'NextTrack': 'Next Track'
                }
    def broken(self):
        logger.warning(""" pywinauto.application.Application().connect() doesn't seem to work for me, so this controller doesnt work
                       I'm going to fix it one day, but Idk when.""")
        return 

    def event_handler(self, event):
        self.broken()
    def press(self):
        self.broken()
      
class _YTMusicController_linux:
    """A Controller Class for Youtube Music app, I might be able to use the same methoda as the spotify controller, but not right now.
    I navent event used YT music after setting up the controller.
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
                
    def broken(self):
        # logger.warning("""pywinauto.application.Application().connect() doesn't seem to work for me, so this controller doesnt work
                    #    IDK if im going to fix this""")
        raise PendingDeprecationWarning("""pywinauto.application.Application().connect() doesn't seem to work for me, so this controller doesnt work
                       IDK if im going to fix this""")
    
    def event_handler(self, event):
        self.broken()

    def press(self):
        self.broken()

if sys.platform == 'win32':
    SpotifyController = _SpotifyController_win32
    ChromeController = _ChromeController_win32
    YTMusicController = _YTMusicController_win32
    get_focused = _get_focused
elif sys.platform == 'linux':
    SpotifyController = _SpotifyController_linux
    ChromeController = _ChromeController_linux
    YTMusicController = _YTMusicController_linux