#from . import setup
from setup import logger, send_notification, file_dir, config, version, plat
#config = setup.config
import macros
import pystray
from PIL import Image
import threading
import serial.tools.list_ports
import time
import json

Spotify = macros.SpotifyController()
FireFox = macros.FireFoxController()

class MacroDriver:
    def __init__(self, baud_rate = 115200, mode = 1):
        self.baud_rate = baud_rate
        self.mode = mode
        self.port = None
        self.run = True
        self.pause_state = False
        self.focused_window_hwnd = None
        self.channel = None
        self.device = "KB2040 - CircuitPython"
             
    def update_mode(self):
        self.mode += 1
        if self.mode == 3:
            self.mode = 1
        logger.info(f'Mode is now {self.mode}')

    # It is to prevent my dad from pressing all the buttons and messing things up
    def on_pause(self, state):
        logger.info(f'Pause is set to: {state}')
        self.pause_state = state
        
    def change_pause_state(self):
        #self.pause_state = not self.pause_state
        if self.pause_state:
            self.pause_state =  False
            color = (0,0,0)
            
        else:
            self.pause_state = True
            color = (255,0,0)
                    
        data = {"color": [13,color]}
        self.write_serial(data)
        logger.info(f'Pause is set to: {self.pause_state}')

    def stop(self):
        self.run = False 
        if self.serial_port:
            self.serial_port.close()

    def find_device_serial_port(self, name):
        device_ports = [port.device 
                        for port in serial.tools.list_ports.comports()
                        if name in port.description]
        return device_ports
    
    def setup_serial(self):
        """
        Helper to connect and reconnet to the serial channel
        """
        
        if self.port is None:
            logger.info("getting port")
            ports = self.find_device_serial_port(self.device)
            
            #if not ports:
            if len(ports) == 0:
                logger.info('No KB2040 found in comports. Retrying in 5 seconds...')
                time.sleep(5)
                self.setup_serial()
                # continue    
            elif len(ports) > 0:
                self.port = ports[0]
                
        try:
            #global channel
            if self.channel is None:
     
                self.channel = serial.Serial(self.port, self.baud_rate)
                self.channel.timeout = 0.05
                
                logger.info(f'Connected to serial port {self.port} at {self.baud_rate} baud')
                send_notification(title='Connected', msg='Connected to Arduino succesfully!')
       
        except serial.serialutil.SerialException:
            # logger.warning("SerialException(2, could not open port")
            # self.port = None    
            logger.critical('Arduino is already connected to something, shutingdown')
            send_notification(title='Access is denied', msg='Access is denied! Arduino is already connected to something', urgency='critical')
            self.stop()    
            
        # except IndexError:
        #     logger.warning("The Microcontroller is not connected to the computer")
                
        except FileNotFoundError as ex:
            logger.warning(ex)
            self.port = None
            
        
        except Exception as ex:
            logger.warning(ex)
            self.channel = None
                
        return self.channel

    def error_serial(self):
        """
        Helper to handle serial errors
        """
        logger.error("Exception on read, did the board disconnect?")
        #global channel
        if self.channel is not None:
            logger.error("Closing Connection to Microcontroller.")
            self.channel.close()
            self.channel = None
        
            logger.error("Changing serial Port Variable, will have to get new one.")
            
            self.port = None

    def read_serial(self):
        while self.run:
            self.setup_serial()
            
            line = None
            try:
                #receives data from microcontroller
                line = self.channel.readline()[:-2]
            except KeyboardInterrupt:
                logger.critical("KeyboardInterrupt - quitting")
                exit()
                
            except Exception as ex:
                logger.error(ex)
                #logger.error("The Microcontroller probably disconected.")    
                self.error_serial()
                time.sleep(1)
                continue

            if line != b"":
                try:
                    data = json.loads(line.decode("utf8"))
                except Exception as ex:
                    logger.warning(ex)
                    data = {"raw": line.decode("utf8")}
                    #print(data)
            
                if "raw" in data:
                    logger.debug(data)
                    continue

                if 'Button_id' in data and data['Button_id'] == 12:
                #if data['Button_id'] == 12:
                    logger.debug('button 12 was pressed and pause state is true')
                    self.change_pause_state()
                    continue
                
                if self.pause_state:
                    logger.info('pause_state was set to True, ignoring button press')
                    continue
                
                if 'Button_id' in data and data['Button_id'] == 'Mode':
                # if data['Button_id'] == 'Mode':
                    self.update_mode()
                    continue
                
                self.Event_handler(data, self.mode)
                # self.Event_handler(data, self.mode)
                      
    def Event_handler(self, event_data, mode):        
        #logger.(f"{self.mode, button, event_type, layers}")
        logger.info(f"{event_data}, {mode}")
        
        if plat == 'linux':
            focused_window_data = macros.get_focused_window_info()
            window_title = focused_window_data['name']
        
            seperators = [' - ', ' — ']
            for sep in seperators:
                if sep in window_title:
                    split_window_title = window_title.split(sep)
                    window_title = split_window_title[-1]
                    break
            else:
                if focused_window_data['class'] in window_title.lower():
                    window_title = focused_window_data['class']
                elif "Desktop" in window_title:
                    window_title = 'Desktop'
                # else:
                #     print(focused_window_data['class_name'])
                #     print(focused_window_data['class'])
            
            app_data = {"app": window_title, "hwnd": focused_window_data['id']}    
            # print(window_title)
            
        elif plat == 'win32':
            focused_window_title, focused_window_hwnd = macros.get_focused_name()
        
            if isinstance(focused_window_title, tuple):
                focused_window_title = focused_window_title[0]
            
            #THIS IS GROSS, redo this
            if focused_window_title is None or len(focused_window_title) == 0:
                app = 'Desktop'

            else:
                split_focused_window = focused_window_title.split(" - ")
                        
                if len(split_focused_window) == 1:
                
                    split_focused_window = focused_window_title.split(" — ")
                
                    if len(split_focused_window) == 1:
                        split_focused_window = focused_window_title.split(" ")

                app = split_focused_window[-1]
                app= app.strip('\n')
        
            app_data = {"app": app, "hwnd": focused_window_hwnd}
        
        # print(app_data)
        logger.debug(app_data)
        if 'Encoder' in event_data:
            Encoder_handler(event_data, mode, app_data)
            
        elif "Button_id" in event_data:
            Button_handler(event_data, mode, app_data)

    def write_serial(self, data):
        """
        Loop on a data provider (here a user prompt) and send the data.
        """
        self.setup_serial()
        try:
            self.channel.write(json.dumps((data)).encode())
            self.channel.write(b"\r\n")
            
        except Exception as ex:
            print(ex)
            self.error_serial()

    # def change_RGB(self, pixels, color):
    #     data = {"color": [pixels,color]}
        
    #     self.write_serial(data)

def Encoder_handler(event_data, mode, app_data):
    encoder_data = event_data['Encoder'][0]
    if 'Layers' in event_data:
        layers = event_data['Layers']
    else:
        layers = []
        
    app = app_data['app']
    #focused_window_hwnd = app_data['hwnd']    
    
    # encoder = encoder_data['Id']
    # event_type = encoder_data['Value']

    # print(app, encoder_data['Id'], encoder_data['Value'], layers)
    match [app, encoder_data['Id'], encoder_data['Value'], layers]:
        #######################################    Encoder 1    ########################################
        case [_, 1, "RL", []]:
            logger.debug('VolumeDown')
            threading.Thread(target=Spotify.event_handler, args=('VolumeDown',)).start()    
        
        case [_, 1, "RR", []]:
            logger.debug('VolumeUp')
            threading.Thread(target=Spotify.event_handler, args=('VolumeUp',)).start()    
        
        case [_, 1, "RLB", []]:
            logger.debug('Back5s')
            threading.Thread(target=Spotify.event_handler, args=('Back5s',)).start()    
        
        case [_, 1, "RRB", []]:
            logger.debug('Forward5s')
            threading.Thread(target=Spotify.event_handler, args=('Forward5s',)).start()    

        ########################################    Encoder 2    ########################################
        case ['LibreOffice Draw', 2, "RL", []]:
            logger.debug('Encoder2 rotate left, zoming out')
            macros.libreOffice_zoomout()
    
        case ['LibreOffice Draw', 2, "RR", []]:
            logger.debug('Encoder2 rotate right, zoming in')
            macros.libreOffice_zoomin()
        
        case ['LibreOffice Draw', 2, "RLB", []]:
            logger.debug('Encoder2 rotate left, w/ button font_size_down')
            macros.libreOffice_font_size_down()
        
        case ['LibreOffice Draw', 2, "RRB", []]:
            logger.debug('Encoder2 rotate right w/ button, font_size_up')
            macros.libreOffice_font_size_up()
        
    
        
        # case ['factorio', 2, "RL", []]:
        #     logger.debug('Encoder2 rotate left, Increase area')
        #     macros.perform_press('add')
    
        # case ['factorio', 2, "RR", []]:
        #     logger.debug('Encoder2 rotate right, decrease area')
        #     macros.perform_press('subtract')
        
        
        
        ###TEMPORARY
        case [_, 2, "RL", [2]]:
            logger.debug('Encoder2 rotate left, zoming out')
            macros.perform_press('left')
    
        case [_, 2, "RR", [2]]:
            logger.debug('Encoder2 rotate right, zoming in')
            macros.perform_press('right')   

        
        case [_, 2, "RL", []]:
            logger.debug('Encoder2 rotate left, zoming out')
            macros.perform_hotkey(['ctrl', '-'])
    
        case [_, 2, "RR", []]:
            logger.debug('Encoder2 rotate right, zoming in')
            macros.perform_hotkey(['ctrl', '='])  
            """
            I did 'ctrl' + '=', because the + symbol requires the Shift key
            so what happens is 'ctrl' + 'shift' + '=' to get 'ctrl' + '+'
            and in adobe acrobat pdf extension, 'ctrl' + 'shift' + '=' rotates the page.
            """

        case [_, 2, "RR", ["Mode"]]:
            logger.debug('Encoder2 rotate right with mode, reseting zoom')
            macros.perform_hotkey(['ctrl', '0'])  

        case [_, 2, "RLB", []]:
            logger.debug('Encoder2 rotate left w/ button, left arrow')
            macros.perform_press('left')

        case [_, 2, "RRB", []]:
            logger.debug('Encoder2 rotate right w/ button, right arrow')
            macros.perform_press('right')  

def Button_handler(event_data, mode, app_data):

    if 'Layers' in event_data:
        layers = event_data['Layers']
    else:
        layers = []
        
    app = app_data['app']
    focused_window_hwnd = app_data['hwnd']    
    #print(app, mode, event_data['Button_id'], layers)
    
    match [app, mode, event_data['Button_id'], layers]:
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
            macros.moveAppAccrossDesktops(focused_window_hwnd, 'Left')
            
        case [_, mode, 1, [4]]: 
            logger.debug("Moves currently foccused to the virtual Desktop on the right")
            macros.moveAppAccrossDesktops(focused_window_hwnd, 'Right')    
                
        case [_, mode, 2, []]: # any app, any mode and no layers
            logger.debug("Btn 2, no layers")
            threading.Thread(target=Spotify.press, args=()).start()    

        case [_, mode, 2, [1]]: # any app, any mode and btn 1 as layer
            logger.debug("Btn 2, btn 1 as layer")
            threading.Thread(target=FireFox.press, args=()).start() 
        
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
            macro_driver.change_pause_state()

        # Specific app and Any Mode

        # # TEST
        # case ["Destiny 2", mode, 5, []]: # Rocket Flying Test
        #     #left clicks, then presses q, then moves mouse down 15 pixels
        #     logger.debug("Rocket Flying Test")
        #     macros.rocket_flying()

        # case ["Destiny 2", mode, 6, []]: # Wellskate Test
        #     macros.wellskate()

        case ['factorio', mode, 7, []]:
            logger.debug('Increase area factorio')
            macros.perform_press('add')
    
        case ['factorio', mode, 8, []]:
            logger.debug('decrease area factorio' )
            macros.perform_press('subtract')
        
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

        # Any App, Specific Mode
        case [_, 2, 5, []]:     # Cut (Ctrl + x)
            logger.debug("Audacity Cut (Ctrl + x)")
            macros.perform_hotkey(['ctrl', 'x'])

        case [_, 2, 6, []]:     # Audacity Split Ctrl + i 
            logger.debug("Audacity Split (ctrl + i)")
            macros.perform_hotkey(['ctrl', 'i'])       

        case [_, 2, 9, []]:     # Backspace
            logger.debug("Backspace")               
            macros.perform_press(['backspace'])


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
            macros.start_task_viwer()
            #macros.perform_hotkey(['ctrl', 'shift', 'esc'])

        case [_, mode, 11, []]:   #image to text             is button 11
            logger.debug("Image to text")
            threading.Thread(target = macros.Image_to_text2).start()
    

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
    if config['system_tray_icon']:
        threading.Thread(target = sysIcon, daemon=True).start()
    global macro_driver
    # Create a new macro driver
    macro_driver = MacroDriver()

    # Start the macro driver
    macro_driver.read_serial()
    # macro_driver.start()

if __name__ == '__main__':
    main()

    """
    TODO:
        try and transition all pyautogui keyboard funtions to custom_keyboard
        add a write function to custom_keyboard
    """

