"""
All the linux specific stuff will be moved here
Use subprocess.popen instead of os.system
"""
from setup import logger, spotify_auto_start, send_notification
import time
import subprocess
from pynput import mouse, keyboard

import pyautogui
from PIL import ImageGrab
import pytesseract
import pyclip
import os

from mpris2 import Player, get_players_uri

logger.debug(f'Initializing {__file__}')

""" TODO
implement thee rest of the macros

"""
##https://manpages.ubuntu.com/manpages/trusty/man1/xdotool.1.html 

def _send_Command(cmd, is_shell=True, is_text=True):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=is_shell, text=is_text)
    return proc.communicate()
    
def _get_app_ids(app_name:str, only_visible=True):
    """does exactly what it says
    Args:
        app_name (str): the name of th app

    Returns:
        list[str]: a list of the app_ids
    """
    if only_visible:
        cmd = f'xdotool search --classname --onlyvisible {app_name}'
    else:
        cmd = f'xdotool search --classname {app_name}'
    app_ids, _=  _send_Command(cmd)
    apps = app_ids.split()
    return apps

def _CurrentDesktopNumber():
    return int(_send_Command("xdotool get_desktop")[0])

def _get_focused():
    val = _send_Command("xdotool getactivewindow")[0]
    if val == '':
        val is None
    else:
        val = int(val)
    return val

def _get_focused_name():
    # this isnt reliable when on wayland :(
    win_id= _get_focused()
    return _send_Command(f"xdotool getwindowname {win_id}"), win_id

def _GetWindowDesktopNumber(win_id):
    #get_desktop_for_window    
    # cmd = f"xdotool get_desktop_for_window {win_id}"
    # proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
    #val = _send_Command(f"xdotool get_desktop_for_window {win_id}")[0]
    # print(val := _send_Command(f"xdotool get_desktop_for_window {win_id}")[0])
    if val := _send_Command(f"xdotool get_desktop_for_window {win_id}")[0]:
        return int(val)
    
    return _CurrentDesktopNumber()
    
    # return int(val)
    #return _send_Command(f"xdotool get_desktop_for_window {win_id}")

def _get_focused_window_info(geometry = False):
    """
    Returns the Name and the ID of the focused window.
    add geometry = True to get geometry info
    
    Use xwininfo to get info on a window
    xprop too
    return a dict with all info
    """
    active_window_id = int(_send_Command("xdotool getactivewindow")[0])
    focused_window_id = int(_send_Command("xdotool getwindowfocus")[0])
    
    if active_window_id != focused_window_id:
        logger.warning(f"something is wrong, {active_window_id} != {focused_window_id}")
        return 0
    
    window_hex_id = hex(active_window_id)

    window_data = {
        #"name": None,
        #"class_name": None,
        # "class": None,
        "id": int(active_window_id), 
        #"pid": None,
        #"geometry": None
    }
    
    window_name = _send_Command(f"xdotool getwindowname {active_window_id}")[0]
    window_class = _send_Command(f"xdotool getwindowclassname {active_window_id}")[0]
    
    window_data["name"] = window_name.rstrip()
    window_data["class"] = window_class.rstrip()
    
    """Use xprop to get some info"""
    xprop = _send_Command(f"xprop -id {window_hex_id} WM_NAME WM_CLASS _NET_WM_PID")[0]    
    xprop = xprop.split("\n")
    xprop = [i.replace('"', '') for i in xprop]
    # print(xprop)
 
    
    """
    WM_NAME(UTF8_STRING) = ~macro_keyboard - Visual Studio Code
    Splits at ' = '  ->  ['WM_NAME(UTF8_STRING)', '"macro_keyboard - Visual Studio Code"']
    then takes the last item in the list from the split  -> '"macro_keyboard - Visual Studio Code"'
    and puts it in the ditctionary
    """    
    # window_data["name"] = xprop[0].split(" = ")[-1]
    window_data["class_name"] = xprop[1].split(" = ")[-1]
    window_data["pid"] = xprop[2].split(" = ")[-1]
    
    window_data["class_name"] = window_data["class_name"].split(', ')


    if geometry:
        """Use xwininfo to get more info"""
        xwininfo = _send_Command(f"xwininfo -id {window_hex_id}")[0]
        xwininfo = xwininfo.split("\n")
        info_i_want = ['width', 'height', 'corners', 'geometry']
        for item in xwininfo:
            item = item.lower()
            if "border width" in item:
                continue 
            for info in info_i_want:
                if info in item:
                    x = item.split(': ')[-1]
                    window_data[info] = x
        window_data['geometry'] = window_data['geometry'].split(" ")[-1]
        
    # print(window_data)
    return window_data

def _is_app_alive(name: str) -> list[dict[str:str]]:
    """Finds if an app is alive/running using: 
        "wmctrl -lx | grep app_name"
    Will return None if the app is not alive/running

    Args:
        name (str): the name of the app you want to find

    Returns:
        list[dict[str:str]]:  list of dictionaries with keys: 'id', 'desktop', 'class', 'client_machine', 'title'
    """
    
    dictionary_keys = ['id', 'desktop', 'class', 'client_machine', 'title']
    apps_with_name = _send_Command(f'wmctrl -lx | grep {name.lower()}')[0]
    # apps_with_name = _send_Command('wmctrl -lx')[0]
    
    apps_with_name = apps_with_name.splitlines()
    if len(apps_with_name) == 0:
        return 0
    
    for app in apps_with_name:
        # Splits the string every space and adds to list if the lenght is not 0
        app = [item for item in app.split(" ") if len(item) != 0]
        
        # this merges the title of the app back together and puts it at index 4 in the list. 
        # Then removes everything from index 5 to the end of the list
        title = ' '.join(app[4::])
        app[4] = title
        del app[5::]
        
      
        # combines the two list into a dict
        app_dict = dict(zip(dictionary_keys, app ))
    
    return app_dict 

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

# def _media_player_dbus(name):
#     """Returns the dbus object of the app specified
#     will return none if ther is nothing
#     Args:
#         name (str): name of the app, ie: firefox, spotify
#     Returns:
#         ProxyObjectClass: media_player_obj
        
#     """#ProxyObjectClass, Interface: media_player_obj, media_player_iface
#     name = 'org.mpris.MediaPlayer2.' + name.lower()
#     for service in dbus.SessionBus().list_names():
#         if service.startswith(name):
#             media_player_obj = dbus.SessionBus().get_object(service, "/org/mpris/MediaPlayer2")
#             #media_player_iface = dbus.Interface(media_player_obj, dbus_interface='org.mpris.MediaPlayer2.Player')
#             # print(service, media_player_obj)
#             return media_player_obj#, media_player_iface
    
#     return None#, None

#############################################     Macros that can be called     #############################################

# class _MasterMediaController:
#     """A Master Controller Class"""
#     # https://stackoverflow.com/questions/67549618/discrepancy-between-dbus-send-and-pythons-dbus-using-spotify
#     # https://stackoverflow.com/questions/23324841/using-org-mpris-mediaplayer2-player-playbackstatus-property-in-python
#     def __init__(self, media_player_name):
#         self.media_player_name = media_player_name
#         self.actions = {
#                 'PrevTrack': 'Previous Track',
#                 'SeekBackward': 'Seek Backward',
#                 'PlayPause': 'Play Pause',
#                 'SeekForward': 'Seek Forward',
#                 'NextTrack': 'Next Track'
#                 }
        
#         self.mediaTimer = MediaTimer()

#     def _get_all_properties(self, media_player_obj): 
#         return media_player_obj.GetAll('org.mpris.MediaPlayer2.Player', dbus_interface='org.freedesktop.DBus.Properties')

#     def _get_property(self, media_player_obj, prop_name):
#         return media_player_obj.Get('org.mpris.MediaPlayer2.Player', prop_name, dbus_interface='org.freedesktop.DBus.Properties')
 
#     def _set_property(self, media_player_obj, prop_name, value):
#         return media_player_obj.Set('org.mpris.MediaPlayer2.Player', prop_name, value, dbus_interface='org.freedesktop.DBus.Properties')
   
#     def event_handler(self, event):
#         if media_player_obj := _media_player_dbus(self.media_player_name):
#             logger.debug(f"{self.media_player_name} is running")
#             media_player_iface = dbus.Interface(media_player_obj, dbus_interface='org.mpris.MediaPlayer2.Player')
#             if event == "PlayPause":
#                 media_player_iface.PlayPause()
                
#             elif event == "NextTrack":
#                 media_player_iface.Next()

#             elif event == "PrevTrack":
#                 media_player_iface.Previous() 
            
#             elif event in ['VolumeUp', 'VolumeDown']:
#                 volume = float(self._get_property(media_player_obj, 'Volume'))
                
#                 if event == 'VolumeUp':
#                     volume += 0.05
#                 else:
#                     volume -= 0.05
                
#                 if volume > 1.0:
#                     logger.debug("vol is greater then 1")
#                     return
          
#                 self._set_property(media_player_obj, 'Volume', volume)
            
#             elif event == "Back5s":
#                 media_player_iface.Seek(-5000000)
#             elif event == "Forward5s":
#                 media_player_iface.Seek(5000000)

#         else:
#             logger.debug(f"{self.media_player_name} is NOT running, ignoring msg")

            
#     def press(self):
#         if result := self.mediaTimer.press_button():
#             logger.debug(result)
#             self.event_handler(result)    
 
# class _SpotifyController(_MasterMediaController):
#     def __init__(self):
#         _MasterMediaController.__init__(self, 'spotify')
        
#         self.spotify_window_id = None
#         if spotify_auto_start:
#             if not _media_player_dbus('spotify'):
#                 logger.info("Launching Spotify")
#                 self._startSpotify()
                
#     def _startSpotify(self):
#         # I just made a shortcut for spotify
#         pyautogui.hotkey("ctrl", 'alt', 'shift', 'p')
#         time.sleep(0.4)

#     def move_spotify_window(self, direction):
#         if not self.spotify_window_id:
#             window_ids = _get_app_ids('Spotify', only_visible=False)
#             for win_id in window_ids:
#                 stdout, stderr = _send_Command(f"xdotool getwindowpid {win_id}")
#                 if stdout and not stderr:
#                     self.spotify_window_id= int(win_id)
#                     break
                
#         stdout, stderr = _moveAppAccrossDesktops(app_id=self.spotify_window_id, movement=direction)
#         #logger.debug(stdout, stderr)
 

    
# BRAND NEW    
class _MasterMediaController:
    """A Master Controller Class"""
    # https://github.com/hugosenari/mpris2
    def __init__(self, media_player_name):
        self.media_player_name = media_player_name
        self.actions = {
                'PrevTrack': 'Previous Track',
                'SeekBackward': 'Seek Backward',
                'PlayPause': 'Play Pause',
                'SeekForward': 'Seek Forward',
                'NextTrack': 'Next Track'
                }
        
        self.mediaTimer = MediaTimer()
        self.dbus_uri = self._get_dbus_uri()
        self.media_player = self._set_player()
    
    def _get_dbus_uri(self):
        for uri in get_players_uri():
            if self.media_player_name in uri:
                return uri
        logger.debug(f"There is no dbus_uri with {self.media_player_name}")
    
    def _set_player(self):
        try:
            # media_player = Player(dbus_interface_info={'dbus_uri': f'org.mpris.MediaPlayer2.{self.media_player_name}'})
            media_player = Player(dbus_interface_info={'dbus_uri': self.dbus_uri})
            return media_player
        except Exception as e:
            logger.warning(e)
    
    # def _get_all_properties(self, media_player_obj): 
        # return media_player_obj.GetAll('org.mpris.MediaPlayer2.Player', dbus_interface='org.freedesktop.DBus.Properties')

    # def _get_property(self, media_player_obj, prop_name):
    #     return media_player_obj.Get('org.mpris.MediaPlayer2.Player', prop_name, dbus_interface='org.freedesktop.DBus.Properties')
 
    # def _set_property(self, media_player_obj, prop_name, value):
    #     return media_player_obj.Set('org.mpris.MediaPlayer2.Player', prop_name, value, dbus_interface='org.freedesktop.DBus.Properties')
   
    def event_handler(self, event):
        try:
            if self.media_player:
                
                # logger.debug(f"{self.media_player_name} is running")
            
                if event == "PlayPause":
                    self.media_player.PlayPause()
                    
                elif event == "NextTrack":
                    self.media_player.Next()

                elif event == "PrevTrack":
                    self.media_player.Previous()
                
                elif event in ['VolumeUp', 'VolumeDown']:
                    volume = self.media_player.Volume
                    # volume = round(volume,2)
                    logger.debug(f'current volume: {volume}')
       
                    if event == 'VolumeUp':
                        new_volume = volume + 0.05
                    else:
                        new_volume = volume - 0.05
            
                    if new_volume >= 1.0 and volume == 1.0:
                        if volume == 1.0:
                            logger.debug("vol is greater then 1")
                            return
                        
                        elif volume < 1.0:
                            new_volume == 1.0  
                            
                    elif new_volume < 0.0 and volume == 0.0:
                        if volume == 0:
                            logger.debug("vol is less then 1 1")
                            return
                        elif volume > 0.0:
                            new_volume == 0.0
                            
                    new_volume = round(new_volume,2)
                    logger.debug(f'setting volume to: {new_volume}')
                    self.media_player.Volume =  new_volume
                    
                elif event == "Back5s":
                    self.media_player.Seek(-5000000)
                elif event == "Forward5s":
                    self.media_player.Seek(5000000)

            else:
                logger.debug(f"{self.media_player_name} is NOT running, ignoring msg")
        except Exception as e:
            logger.info(e)
            logger.info(f"{self.media_player_name} Is Not running, ignoring msg")

    def _bypass_press(self, action):
        """This Should only be used to test. 
        
        Bypass the press() function and send actions directly to event_handler()
 
        Args:
            action (str): the action you want to happen, can be :
            'PlayPause'
            'NextTrack'
            'PrevTrack'
            'VolumeUp'
            'VolumeDown'
            'Back5s'
            'Forward5s'
        """
        self.event_handler(action)
            
    def press(self):
        if result := self.mediaTimer.press_button():
            logger.debug(result)
            self.event_handler(result)
            # self.event_handler(result)    
 
class _SpotifyController(_MasterMediaController):
    def __init__(self):
        
        if spotify_auto_start:
            if _is_app_alive('spotify') == 0:
                logger.info("Launching Spotify")
                self._startSpotify()
            else:
                logger.info("Spotify is running")
        
        _MasterMediaController.__init__(self, 'spotify')
                
    def _startSpotify(self):
        # I just made a shortcut for spotify
        pyautogui.hotkey("ctrl", 'alt', 'shift', 'p')
        time.sleep(0.4)

class _FireFoxController(_MasterMediaController):
    def __init__(self):
        _MasterMediaController.__init__(self, 'firefox')
                     
class _ChromeController:
    """A Controller Class for Chrome  IT is currently broken
    """
    def __init__(self):
        logger.warning(""" pywinauto.application.Application().connect() doesn't seem to work for me, so this controller doesnt work
                       I̶'m̶ g̶o̶i̶n̶g̶ t̶o̶ f̶i̶x̶ i̶t̶ o̶n̶e̶ d̶a̶y̶, b̶u̶t̶ I̶d̶k̶ w̶h̶e̶n̶.
                       IDK if I will fix this. i have moved to firefox/librewolf.""")
        self.actions = {
                'PrevTrack': 'Previous Track',
                'SeekBackward': 'Seek Backward',
                'PlayPause': 'Play Pause',
                'SeekForward': 'Seek Forward',
                'NextTrack': 'Next Track'
                }
    def broken(self):
        # logger.warning(""" pywinauto.application.Application().connect() doesn't seem to work for me, so this controller doesnt work
        #                I'm going to fix it one day, but Idk when.""")
        raise NotImplementedError ("""pywinauto.application.Application().connect() doesn't seem to work for me, so this controller doesnt work
                       I̶'m̶ g̶o̶i̶n̶g̶ t̶o̶ f̶i̶x̶ i̶t̶ o̶n̶e̶ d̶a̶y̶, b̶u̶t̶ I̶d̶k̶ w̶h̶e̶n̶.
                       IDK if I will fix this. i have moved to firefox/librewolf.""")

    def event_handler(self, event):
        self.broken()
    def press(self):
        self.broken()
      
class _YTMusicController:
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
        raise NotImplementedError("""pywinauto.application.Application().connect() doesn't seem to work for me, so this controller doesnt work
                       IDK if im going to fix this""")

    def event_handler(self, event):
        self.broken()

    def press(self):
        self.broken()
    
def _perform_hotkey(hotkey):
    logger.debug(f"perform_hotkey {hotkey = }")
    pyautogui.hotkey(hotkey)

def _perform_press(key):
    logger.debug(f"perform_press {key = }")
    pyautogui.press(key)

def _change_desktop(direction:str, focused_app=None): # change desktop hotkey, where direction is either 'left' or 'right'. Will alt+tab if specific program is focused
    """Changes the desktop, moves left or right

    Args:
        direction (str): Either: 'left' or 'right'
        focused_app (str): Does nothing, its here to allow compatibility with the windows version
    """
    # modify so that it will check what the current desktop is and 
    
    logger.debug(f"move desktop {direction}")
    current_window = int(_send_Command("xdotool get_desktop")[0])

    direction = direction.lower()
    
    if direction == 'left':
        if current_window == 0:
            return "Movement Request is ignored"
        cmd = "xdotool set_desktop --relative -- -1"
        
    elif direction == 'right':
        total_desktops = int(_send_Command("xdotool get_num_desktops")[0])
        if current_window +1 == total_desktops:
            return "Movement Request is ignored"
        cmd = "xdotool set_desktop --relative -- 1"
        
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    proc.communicate()

def _moveAppAccrossDesktops(**kwargs):
    """Moves an app accross desktops.
    app_id, movement: str
    moves the specified app_id in some way
    by default is movement is left blank, it will bring the app the to current desktop
    
    if app_id is blank, it will move the focused one

    Movements are:
    'Left': Goes left,
    'Right': Goes Right,
    'Current': Moves to the current desktop
    
    Args:
        app_id (int | str): wind_id of the app
        movement (str): Movement Type

    Returns:
        Nothing at the moment
    """
    if 'app_id' in kwargs:
        app_id = kwargs['app_id']
    else:
        app_id = _get_focused()
        
    if 'movement' in kwargs:
        movement = kwargs['movement'].lower()
    else:
        movement = 'current'
    ### use xdotool
    if not app_id:
        logger.debug("App_id is nothing, so you are focusing the desktop. returning")
        return
    
    logger.debug(f"{app_id=}")
    
    movements = {
            'left': (_GetWindowDesktopNumber(app_id) -1),
            'right': (_GetWindowDesktopNumber(app_id) +1),
            'current':_CurrentDesktopNumber()
            }
    destination = movements[movement]
    return _send_Command(f'xdotool set_desktop_for_window {app_id} {destination}')

def _moveFocusedAppAccrossDesktops(movement):
    """
    #works
    """
    
    # cmd = "xdotool getactivewindow"
    # proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
    focused_app =  _get_focused()
    #print(focused_app)
    _moveAppAccrossDesktops(app_id= focused_app, movement= movement)

def _start_task_viwer():
    """Open System Monitor"""
    _perform_hotkey(["win", "esc"])    

# def _Image_to_text2():
#     """
#     Okay so in this version, if you're linux distro is using spectacle to take screenshots  you will have to configure and make it save to clipboard

#     Presses Win Shift PrtSc to open spectacle mode, waits for mouse release then does tesseract OCR
#     Press Ctrl V to paste text
#     It works but spectacle takes some time too launch
#     """
    
#     m = mouse.Controller()
#     k = keyboard.Controller()

#     def on_release(key):
#         if key == keyboard.Key.esc:
#             logger.debug('esc pressed and released')
#             # Stop listener and the func
#             m.click(mouse.Button.left,1)
#             return False    
        
#     def on_click(x, y, button, pressed):
#         if not pressed:
#             # Stop listener
#             k.press(keyboard.Key.enter)
#             k.release(keyboard.Key.enter)
            
#             return False
    
#     m.click(mouse.Button.left,1)
    
#     time.sleep(0.2)
#     _perform_hotkey(['win', 'shift', 'prtsc'])
    
#     keyboard_listener = keyboard.Listener(
#         on_release=on_release)

#     time.sleep(0.2)

#     keyboard_listener.start()

#     # Collect events until released # is used to block the code until the left mouse button is released
#     with mouse.Listener(on_click=on_click) as listener:
#         listener.join()
        
#     time.sleep(0.1)

#     keyboard_listener.stop()

#     time.sleep(0.3)
#     img = ImageGrab.grabclipboard()
#     #grabs the image from clipboard and converts the image to text.
#     text = pytesseract.image_to_string(img)
#     text = text.replace('\x0c', '')
#     pyclip.copy(text)
#     logger.debug("imt has finished")

def _Image_to_text2():
    """
    Okay so in this version, if you're linux distro is using spectacle to take screenshots  you will have to configure and make it save to clipboard

    Presses Win Shift PrtSc to open spectacle mode, waits for mouse release then does tesseract OCR
    Press Ctrl V to paste text
    It works but spectacle takes some time too launch
    """
    def on_release(key):
        if key == keyboard.Key.esc: # Stop listener and the func
            logger.debug('esc pressed and released')
            pyautogui.click()
            return False    
        
    def on_click(x, y, button, pressed):
        if not pressed: # on release, Stop the listener
            _perform_press('ENTER')
            return False
    
    time.sleep(0.2)
    _perform_hotkey(['win', 'shift', 'prtsc'])
    
    keyboard_listener = keyboard.Listener(
        on_release=on_release)

    time.sleep(0.2)

    keyboard_listener.start()

    # Collect events until released # is used to block the code until the left mouse button is released
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()
        
    time.sleep(0.1)

    keyboard_listener.stop()

    time.sleep(0.3)
    img = ImageGrab.grabclipboard()
    #grabs the image from clipboard and converts the image to text.
    text = pytesseract.image_to_string(img)
    text = text.replace('\x0c', '')
    pyclip.copy(text)
    send_notification(title='Image To Text Successfull', msg='Image To Text has finished', app_name=os.path.basename(__file__))
    logger.debug("imt has finished")


logger.debug(f"Initializing is complete for {__file__}")

