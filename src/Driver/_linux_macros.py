"""
All the linux specific stuff will be moved here
Use subprocess.popen instead of os.system
"""
from setup import logger
import time
import subprocess
logger.debug(f'Initializing {__file__}')

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
    #logger.debug(f"perform_hotkey {hotkey = }")
    raise NotImplementedError
    #custom_keyboard.hotkey(*hotkey)

def _perform_press(key):
    #logger.debug(f"perform_press {key = }")
    #custom_keyboard.press(key)
    raise NotImplementedError

def _change_desktop(direction:str, focused_app=None) -> None: #change desktop hotkey, where direction is either 'left' or 'right'. Will alt+tab if specific program is focused
    """Changes the desktop, moves left or right

    Args:
        direction (str): Either: 'left' or 'right'
        focused_app (str): Does nothing, its here to allow compatibility with the windows version
    """
    logger.debug(f"move desktop {direction}")
    
    direction = direction.lower()
    
    if direction == 'left':
        cmd = 'xdotool set_desktop --relative -- -1'
    elif direction == 'right':
        cmd = 'xdotool set_desktop --relative -- 1'
    #os.system(cmd)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    proc.communicate()

def _moveAppAccrossDesktops(hwnd: int, movement: str) -> int:
    """Moves an app accross desktops.
    
    ### Not implemented
    
    Movements are:
    'Left': Goes left,
    'Right': Goes Right,
    'Current': Moves to the current desktop
    
    Args:
        hwnd (HWND): The HWND(handle) of the app
        movement (str): Movement Type

    Returns:
        Nothing at the moment
    """
    raise NotImplementedError
   
def _Image_to_text2():
    """Presses Win Shift S to open snippet mode, waits for mouse release then does tesseract OCR
    Press Ctrl V to paste text
    """
    #import pytesseract
    
    raise NotImplementedError
    
logger.debug(f"Initializing is complete for {__file__}")