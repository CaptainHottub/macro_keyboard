"""
All the linux specific stuff will be moved here
Use subprocess.popen instead of os.system
"""
from setup import logger
import time
import subprocess
from pynput import mouse, keyboard

import pyautogui
from PIL import ImageGrab
import pytesseract
import pyclip


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
    # https://stackoverflow.com/questions/70737550/how-to-connect-to-mediaplayer2-player-playbackstatus-signal-using-pygtk
    # https://www.reddit.com/r/linuxquestions/comments/mv9z12/how_does_linux_handle_playpause_from_function_keys/
    """Its a controller for spotify.
    add a func to start it.
        
    """
    def __init__(self):
        self.spotify_window_id = None
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
        self._startSpotify()

    def _startSpotify(self):
        # I just made a shortcut for spotify
        app_id = _get_app_ids('Spotify')
        if len(app_id) == 0:
            pyautogui.hotkey("ctrl", 'alt', 'shift', 'p')
    
    # def move_spotify_window_to_current_desktop(self):
    #     """
    #     """
    #     if not self.spotify_window_id:
    #         window_ids = _get_app_ids('Spotify', )

    #         for win_id in window_ids:
    #             cmd = f"xdotool getwindowname {win_id}"
    #             spotify_or_song_name, _blank = _send_Command(cmd)
    #             if len(spotify_or_song_name) > 2 or 'Spotify Premium' in spotify_or_song_name:
    #                 self.spotify_window_id= int(win_id)
    #                 break
        
    #     print(self.spotify_window_id)
    #     _moveAppAccrossDesktops(app_id = self.spotify_window_id)        

    def move_spotify_window(self, direction):
        if not self.spotify_window_id:
            window_ids = _get_app_ids('Spotify', only_visible=False)
            for win_id in window_ids:
                stdout, stderr = _send_Command(f"xdotool getwindowpid {win_id}")
                if stdout and not stderr:
                    self.spotify_window_id= int(win_id)
                    break
                
        stdout, stderr = _moveAppAccrossDesktops(app_id=self.spotify_window_id, movement=direction)
        #logger.debug(stdout, stderr)

    def sendCommand(self, cmd):
        ret_value = _send_Command(cmd, is_shell=False)
        
        if ret_value[0] =='' or ret_value[1] == 'Error org.freedesktop.DBus.Error.ServiceUnknown: The name is not activatable': 
            logger.debug("Spotify is not running, starting it.")
            self._startSpotify()
            time.sleep(1.8)
            return _send_Command(cmd, is_shell=False)
        return ret_value

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
        #print(final_msg)    
        self.sendCommand(final_msg)

    def press(self):
        if result := self.mediaTimer.press_button():
            logger.debug(result)
            self.event_handler(result)
        
class _ChromeController:
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
        # logger.warning(""" pywinauto.application.Application().connect() doesn't seem to work for me, so this controller doesnt work
        #                I'm going to fix it one day, but Idk when.""")
        raise NotImplementedError (""" pywinauto.application.Application().connect() doesn't seem to work for me, so this controller doesnt work
                       I'm going to fix it one day, but Idk when.""")

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

def _Image_to_text2():
    """
    Okay so in this version, if you're linux distro is using spectacle to take screenshots  you will have to configure and make it save to clipboard

    Presses Win Shift PrtSc to open spectacle mode, waits for mouse release then does tesseract OCR
    Press Ctrl V to paste text
    It works but spectacle takes some time too launch
    """
    
    m = mouse.Controller()
    k = keyboard.Controller()

    def on_release(key):
        if key == keyboard.Key.esc:
            logger.debug('esc pressed and released')
            # Stop listener and the func
            m.click(mouse.Button.left,1)
            return False    
        
    def on_click(x, y, button, pressed):
        if not pressed:
            # Stop listener
            k.press(keyboard.Key.enter)
            k.release(keyboard.Key.enter)
            
            return False
    
    m.click(mouse.Button.left,1)
    
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
    logger.debug("imt has finished")

def _start_task_viwer():
    """Open System Monitor"""
    _perform_hotkey(["win", "esc"])
    

logger.debug(f"Initializing is complete for {__file__}")