#from . import setup
from setup import logger, send_notification, file_dir, config, version
#config = setup.config
import macros

import pystray
from PIL import Image
import threading
import serial.tools.list_ports
import time
import sys
import traceback

Spotify = macros.SpotifyController()
class MacroDriver:
    def __init__(self, baud_rate = 19200, mode = 1):
        self.baud_rate = baud_rate
        self.mode = mode
        self.serial_port = None
        self.run = True
        self.pause_state = False
        #self.button = 0
        #self.event_type = ''
        #self.layers = []
        self.focused_window_hwnd = None
        
        #self.Spotify = tools.SpotifyController()
        # self.YTMusic = tools.YTMusicController()
        # self.Chrome = tools.ChromeController()

                
    def update_mode(self):
        self.mode += 1
        if self.mode == 3:
            self.mode = 1
        logger.debug(f'Mode is now {self.mode}')

    # It is to prevent my dad from pressing all the buttons and messing things up
    def on_pause(self, state):
        logger.info(f'Pause is set to: {state}')
        self.pause_state = state
        
    def change_pause_state(self):
        self.pause_state = not self.pause_state
        logger.info(f'Pause is set to: {self.pause_state}')

    def stop(self):
        self.run = False 
        if self.serial_port:
            self.serial_port.close()

    def msgparser(self, msg):
        """
        This parses the message sent by the microcontroller to something useable
        I am quite impressed on how compact this is.

        Args:
            msg (str): A string of Binary

        Returns:
            button_name: Name of the button, str if Mode, or encoders, int for the rest
            event_type: What type of event it is as a str
            layers_int: List of layers
        """
        # defines button names
        button_names = {
            0: "Mode",
            14: "Encoder1",
            15: "Encoder2"}
        
        # defines event names
        events_names = {
            0: "btnPress",     # 0000, 1
            1: "btnRelease",   # 0001, 2
            2: "RL",           # 0010, 3      rotary left w/o button
            3: "RR",           # 0011, 4      rotary right w/o button
            6: "RLB",          # 0110, 6      rotary left w/ button
            7: "RRB"           # 0111, 7      rotary right w/ button
            }

        logger.debug("Parsing message")
        
        # for somereason, in linux, on the first readline the value is something like: "\x1b]0;🐍code.py | 8.2.9\x1b\\ +msg"
        # this one line fixes that
        msg = msg.split('\\')[-1]
    
        # splits the string every 4th character
        *layers_int, event_int, button_int = [int(msg[i:i+4], 2) 
                                              for i in range(0, len(msg), 4)]
    
        # renames the buttons if the key is valid, if not returns button_int
        button_name: str | int = button_names.get(button_int, button_int)
        
        # gets the event type
        event_type: str = events_names[event_int]
        
        layers = layers_int[::-1]
        if len(layers) > 0 and not layers[-1]:
            layers[-1] = "Mode"

        return button_name, event_type, layers

    # I want to rewrite this so it looks better
    def start(self):
        while self.run:
            if not self.serial_port:    # If the serial port is not connected/not defined
                # Look for the device
                arduino_ports = [
                    p.device for p in serial.tools.list_ports.comports()
                    if 'Pico - CircuitPython' in p.description
                ]
            
                if not arduino_ports:
                    logger.info('No Pi Pico found in comports. Retrying in 5 seconds...')
                    time.sleep(5)
                    continue
               
                # Connect to the first available device
                self.com_port = arduino_ports[0]

                try:
                    self.serial_port = serial.Serial(self.com_port, self.baud_rate)
                    logger.info(f'Connected to serial port {self.com_port} at {self.baud_rate} baud')
                    #toaster.show_toast("Connected","Connected to Arduino succesfully!", duration=2, threaded=True)
                    send_notification(title='Connected', msg='Connected to Arduino succesfully!')

                except serial.serialutil.SerialException:
                    logger.critical('Arduino is already connected to something, shutingdown')
                    #toaster.show_toast("Access is denied","Arduino is already connected to something", duration=2, threaded=True)
                    send_notification(title='Access is denied', msg='Access is denied! Arduino is already connected to something', urgency='critical')
                    self.stop()

                except Exception as e:
                    logger.error(f'Error connecting to serial port {self.com_port}: {e}')
                    continue
                
                finally:
                    logger.debug("Waiting for message from microcontroller.")

            else:
                # will have to re write this
                try:
                    # invalid literal for int() with base 10: ''
                    button_string = str(self.serial_port.readline(), 'utf-8').strip()

                    #print(repr(button_string))

                    logger.debug(f"Message has been received: {button_string}")                    
                    #self.button, self.event_type, self.layers = self.msgparser(button_string)
                    button, event_type, layers = self.msgparser(button_string)

                    #print(repr(button),repr(event_type),repr(layers))
                    
                    
                    #logger.debug(f'Message was: {button=}, {event_type=}, {layers=}')
                    
                    if button == "Mode":
                        self.update_mode()
                        continue
                    
                    # if pause_state is True, buttons will be ignored, except for B, it toggles pause_state
                    if not self.pause_state: # Buttons wont be ignored
                        #self.Event_handler()
                        self.Event_handler(button, event_type, layers)


                    elif button == 12:
                        logger.debug('button 12 was pressed and pause state is true')
                        self.change_pause_state()
                    else:
                        logger.info('pause_state was set to True, ignoring button press')

                    # if 'mode button was pressed' in button_string:
                    #     logger.info(button_string)
                    #     continue
                except serial.serialutil.SerialException:
                    logger.error(f'Arduino Micro disconnected from {self.com_port}. Looking for device...')
                    
                    #toaster.show_toast("Arduino Micro disconnected", 
                                    #    f'Arduino Micro disconnected from {self.com_port}. Looking for device...', 
                                    #    duration=2, 
                                    #    threaded=True)
                    
                    self.serial_port = None
                    # this is here so it doesn't throw 5 FileNotFoundError exception
                    time.sleep(0.2) 
                    continue

                except ValueError as e:
                    logger.error(e)
                    logger.error(traceback.format_exc())

                except Exception as exception:
                    logger.warning(f'Exception raised: {exception = }')
                    #logger.error('ValueError, stop() has been called, goodbye...')

        logger.error('PROGRAM is shutting down')
    
    def Encoder_handler(self, app, button, event_type, layers):

        match [app, button, event_type, layers]:
            ########################################    Encoder 1    ########################################
            case [_, "Encoder1", "RL", []]:
                logger.debug('VolumeDown')
                threading.Thread(target=Spotify.event_handler, args=('VolumeDown',)).start()    
            
            case [_, "Encoder1", "RR", []]:
                logger.debug('VolumeUp')
                threading.Thread(target=Spotify.event_handler, args=('VolumeUp',)).start()    
            
            case [_, "Encoder1", "RLB", []]:
                logger.debug('Back5s')
                threading.Thread(target=Spotify.event_handler, args=('Back5s',)).start()    
            
            case [_, "Encoder1", "RRB", []]:
                logger.debug('Forward5s')
                threading.Thread(target=Spotify.event_handler, args=('Forward5s',)).start()    

            ########################################    Encoder 2    ########################################
            case ['LibreOffice Draw', "Encoder2", "RL", []]:
                logger.debug('Encoder2 rotate left, zoming out')
                macros.libreOffice_zoomout()
        
            case ['LibreOffice Draw', "Encoder2", "RR", []]:
                logger.debug('Encoder2 rotate right, zoming in')
                macros.libreOffice_zoomin()
            
            case [_, "Encoder2", "RL", []]:
                logger.debug('Encoder2 rotate left, zoming out')
                macros.perform_hotkey(['ctrl', '-'])
        
            case [_, "Encoder2", "RR", []]:
                logger.debug('Encoder2 rotate right, zoming in')
                macros.perform_hotkey(['ctrl', '='])  
                """
                I did 'ctrl' + '=', because the + symbol requires the Shift key
                so what happens is 'ctrl' + 'shift' + '=' to get 'ctrl' + '+'
                and in adobe acrobat pdf extension, 'ctrl' + 'shift' + '=' rotates the page.
                """

            case [_, "Encoder2", "RR", ["Mode"]]:
                logger.debug('Encoder2 rotate right with mode, reseting zoom')
                macros.perform_hotkey(['ctrl', '0'])  

            case [_, "Encoder2", "RLB", []]:
                logger.debug('Encoder2 rotate left w/ button, left arrow')
                macros.perform_press('left')

            case ["Encoder2", "RRB", []]:
                logger.debug('Encoder2 rotate right w/ button, right arrow')
                macros.perform_press('right')  

    def Button_handlerV3(self, app, button, layers):
        #logger.debug("Button_handlerV2")
        
        match [app, self.mode, button, layers]:
            #Format: 
            #case [AppName, "MacroMode", "ButtonNumber"]:
            # Leave AppName _ for any app
            # MacroMode as mode for any mode
            # Layers is a list of layers where "Mode" will be the last one
            
            # Any app and Any Mode    And that are prioritives 
            case [_, mode, 1, []]:    # Shows what each button is defined as
                logger.debug("ButtonMode")
                threading.Thread(target = macros.ButtonMode, args=(mode, )).start()   

            case [_, mode, 1, [3]]:
                logger.debug("Moves currently foccused to the virtual Desktop on the left")
                macros.moveAppAccrossDesktops(self.focused_window_hwnd, 'Left')
                
            case [_, mode, 1, [4]]: 
                logger.debug("Moves currently foccused to the virtual Desktop on the right")
                macros.moveAppAccrossDesktops(self.focused_window_hwnd, 'Right')    
                    
            case [_, mode, 2, []]: # any app, any mode and no layers
                logger.debug("Btn 2, no layers")
                threading.Thread(target=Spotify.press, args=()).start()    

            # case [_, mode, 2, [1]]: # any app, any mode and btn 1 as layer
            #     logger.debug("Btn 2, btn 1 as layer")
            #     threading.Thread(target=YTMusic.press, args=()).start() 
            
            # case [_, mode, 2, [1, 'Mode']]: # any app, any mode and 'Mode' and btn 1 as layer
            #     logger.debug("Btn 2, btn 1 as layer")
            #     threading.Thread(target=Chrome.press, args=()).start() 
            
            # case [_, mode, 2, ['Mode']]: # any app, any mode and Mode as layer
            #     logger.debug("Like")
            #     #macros.spotifyControl("Like")
            #     threading.Thread(target=Spotify.event_handler, args=('Like',)).start()    
            
            #Spotify
            case [_, mode, 2, [3, 4]]: # any app, any mode and btn 3, 4 as layer
                logger.debug("Moves Spotify to the current virtual Desktop")
                threading.Thread(target=Spotify.move_spotify_window, args=('Current',)).start()    

            case [_, mode, 2, [3]]:
                logger.debug("Moves Spotify to the virtual Desktop on the left")
                threading.Thread(target=Spotify.move_spotify_window, args=('Left',)).start()    
            
            case [_, mode, 2, [4]]: 
                logger.debug("Moves Spotify to the virtual Desktop on the right")
                threading.Thread(target=Spotify.move_spotify_window, args=('Right',)).start()    

            
            case [_, mode, 3, []]:    # move desktop left for any app
                threading.Thread(target = macros.change_desktop, args=('left', app)).start()

            case [_, mode, 4, []]:     # move desktop right for any app   
                threading.Thread(target = macros.change_desktop, args=('right', app)).start()
            



            case [_, mode, 12, []]:     # Pause button press
                logger.debug("Pause button press")
                self.change_pause_state()


            # # TEST
            # case ["Destiny 2", mode, 5, []]: # Rocket Flying Test
            #     #left clicks, then presses q, then moves mouse down 15 pixels
            #     logger.debug("Rocket Flying Test")
            #     macros.rocket_flying()

            # case ["Destiny 2", mode, 6, []]: # Wellskate Test
            #     macros.wellskate()


            # Specific app and Any Mode
            # VS Code Layer
            case ["Visual Studio Code", mode, 5, []]: # run code in Vs code
                logger.debug("run code in Vs code")
                macros.perform_hotkey(['ctrl', 'alt', 'n'])

            # Star Citizen Layer
            case ["Star Citizen", mode, 5, []]: # focus front shields
                macros.sheild_focus_star_citizen("1")

            case ["Star Citizen", mode, 6, []]: # focus back shields
                macros.sheild_focus_star_citizen("2")

            case ["Star Citizen", mode, 7, []]: # Reset shields
                macros.sheild_focus_star_citizen("3")

            # # Any App, Specific Mode
            # case [_, "2", 5]:     # Cut (Ctrl + x)
            #     logger.debug("Audacity Cut (Ctrl + x)")
            #     macros.perform_hotkey(['ctrl', 'x'])

            # case [_, "2", 6]:     # Audacity Split Ctrl + i 
            #     logger.debug("Audacity Split (ctrl + i)")
            #     macros.perform_hotkey(['ctrl', 'i'])       

            # case [_, "2", 9]:     # Backspace
            #     logger.debug("Backspace")               
            #     macros.perform_press(['backspace'])


            # Macros that are last priority.     
            case [_, mode, 5, []]:   # Text to speech
                logger.debug("Text to speech")
                macros.textToSpeech()
                
            case [_, mode, 6, []]:   # Stop Speech
                logger.debug("Stop Speech")
                macros.stopSpeech()

            case [_, mode, 7, []]:   # Copy
                #logger.debug("Copy")
                #NOTE : this can cause a keyboard interupt if used in terminal
                macros.perform_hotkey(['ctrl', 'c'])             

            case [_, mode, 8, []]:   # Paste 
                #logger.debug("Paste")
                macros.perform_hotkey(['ctrl', 'v'])

            case [_, mode, 9, []]:   # Search highlighted text
                #logger.debug("Search highlighted text")
                macros.search_highlighted_text()

            case [_, mode, 10, []]:     # runs Task Manager      is button 10
                logger.debug("Starting Task manager")
                macros.perform_hotkey(['ctrl', 'shift', 'esc'])

            case [_, mode, 11, []]:   #image to text             is button 11
                logger.debug("Image to text")
                threading.Thread(target = macros.Image_to_text2).start()
                
    def Event_handler(self, button, event_type, layers):
            #logger.info(f"{self.button, self.event_type, self.layers}")
            logger.info(f"{button, event_type, layers}")
            focused_window_title, self.focused_window_hwnd = macros.get_focused_name()
            
            if isinstance(focused_window_title, tuple):
                focused_window_title = focused_window_title[0]
                
            if focused_window_title is None or len(focused_window_title) == 0:
                app = 'Desktop'
            else:
                split_focused_window = focused_window_title.split(" - ")
                
                if len(split_focused_window) == 1:
                    split_focused_window = focused_window_title.split(" ")
                    #app = split_focused_window[0]

                else:
                    split_focused_window.reverse()
                app = split_focused_window[0]
                app= app.strip('\n')
                
            if button in ["Encoder1", "Encoder2"]:
                self.Encoder_handler(app, button, event_type, layers)
            
            else:
                self.Button_handlerV3(app, button, layers)


#############################################       This is for setup       ############################################# 

def sysIcon():
    """
    The icon for the widget will live in # '/macro_keyboard/Images/pythonIcon.ico'
    
    """ 
    if config['system_tray_icon_image_path_relative'] and config['system_tray_icon_image_path'] == '':
        icon_path = fr"{file_dir}{config['system_tray_icon_image_path_relative']}"

    elif config['system_tray_icon_image_path'] and config['system_tray_icon_image_path_relative'] == '':
        icon_path = config['system_tray_icon_image_path']
    
    image = Image.open(icon_path)
    systray = pystray.Icon(name="Python Macro", icon=image, title=f"Python Macro {version}", menu=pystray.Menu(
        pystray.MenuItem("Quit", lambda: macro_driver.stop())
    ))
    
    systray.run()
    logger.debug("System Tray Icon started Sucessfully")

def main():
    logger.debug(f"Initializing {__file__} version: {version}")
    
    if config['system_tray_icon']:
        threading.Thread(target = sysIcon, daemon=True).start()


    global macro_driver
    # Create a new macro driver
    macro_driver = MacroDriver()

    # Start the macro driver
    macro_driver.start()

if __name__ == '__main__':
    
    plat = sys.platform.lower()
    if plat[:5] == 'linux':
        logger.warning("Some features may not work")
        #toaster.show_toast("Warning", "Some features may not work on Linux", duration=2, threaded=True)
        #send_notification(title='Warning', msg='Some features may not work on Linux')

    main()

    """
    TODO:
        try and transition all pyautogui keyboard funtions to custom_keyboard
        add a write function to custom_keyboard
    """

