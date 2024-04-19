from logger import logger, toaster
import tools
import serial.tools.list_ports
import threading
import time

class MacroDriver:
    def __init__(self, baud_rate = 19200, mode = 1):
        self.baud_rate = baud_rate
        self.mode = mode
        self.serial_port = None
        self.run = True
        self.pause_state = False
        self.button = 0
        self.event_type = ''
        self.layers = []

    # add a mode function to this
    # when called it increases the mode by 1 then at 3 it resets to 1
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

        # splits the string every 4th character
        *layers_int, event_int, button_int = [int(msg[i:i+4], 2) for i in range(0, len(msg), 4)]
    
        # renames the buttons if the key is valid 
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
                    if 'Pi Pico Macro Driver' in p.description
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
                    toaster.show_toast("Connected","Connected to Arduino succesfully!", duration=2, threaded=True)

                except serial.serialutil.SerialException:
                    logger.critical('Arduino is already connected to something, shutingdown')
                    toaster.show_toast("Access is denied","Arduino is already connected to something", duration=2, threaded=True)
                    self.stop()

                except Exception as e:
                    logger.error(f'Error connecting to serial port {self.com_port}: {e}')
                    continue

            else:


                # will have to re write this
                try:
                    button_string = str(self.serial_port.readline(), 'utf-8').strip()

                    self.button, self.event_type, self.layers = self.msgparser(button_string)

                    if self.button == "Mode":
                        self.update_mode()
                        continue
                    
                    # if pause_state is True, buttons will be ignored, except for B, it toggles pause_state
                    if not self.pause_state: # Buttons wont be ignored
                        #self.Button_handlerV3(btn, event_type, layers)
                        #self.Event_handler(btn, event_type, layers)
                        self.Event_handler()


                    elif self.button == 12:
                        logger.debug('button 12 was pressed and pause state is true')
                        self.change_pause_state()
                    else:
                        logger.info('pause_state was set to True, ignoring button press')

                    # if 'mode button was pressed' in button_string:
                    #     logger.info(button_string)
                    #     continue

                    # #logger.debug(f'Received button event: {button_string}')
                    # button_string = button_string[-3:]
                    # button, macro_mode = button_string.split(".")

                    # # Call Button_handler() with button_string as an argument
                    # #self.Button_handler(button, macro_mode)
                    # self.Button_handlerV2(button, macro_mode)

                except serial.serialutil.SerialException:
                    logger.error(f'Arduino Micro disconnected from {self.com_port}. Looking for device...')
                    
                    toaster.show_toast("Arduino Micro disconnected", 
                                       f'Arduino Micro disconnected from {self.com_port}. Looking for device...', 
                                       duration=2, 
                                       threaded=True)
                    
                    self.serial_port = None
                    # this is here so it doesn't throw 5 FileNotFoundError exception
                    time.sleep(0.2) 
                    continue

                except ValueError as e:
                    logger.error(e)

                except Exception as exception:
                    logger.warning(f'Exception raised: {exception = }')
                    #logger.error('ValueError, stop() has been called, goodbye...')

        logger.error('PROGRAM is shutting down')
    

    def Encoder_handler(self):
        #print(self.button, self.event_type, self.layers)

        match [self.button, self.event_type, self.layers]:
            ########################################    Encoder 1    ########################################
            case ["Encoder1", "RL", []]:
                logger.debug('VolumeDown')
                tools.spotifyControl("VolumeDown")
            
            case ["Encoder1", "RR", []]:
                logger.debug('VolumeUp')
                tools.spotifyControl("VolumeUp")
            
            case ["Encoder1", "RLB", []]:
                logger.debug('Back5s')
                tools.spotifyControl("Back5s")
            
            case ["Encoder1", "RRB", []]:
                logger.debug('Forward5s')
                tools.spotifyControl("Forward5s")

            ########################################    Encoder 2    ########################################
            case ["Encoder2", "RL", []]:
                logger.debug('Encoder2 rotate left, zoming out')
                tools.perform_hotkey(['ctrl', '-'])
        
            case ["Encoder2", "RR", []]:
                logger.debug('Encoder2 rotate right, zoming in')
                tools.perform_hotkey(['ctrl', '='])  
                """
                I did 'ctrl' + '=', because the + symbol requires the Shift key
                so what happens is 'ctrl' + 'shift' + '=' to get 'ctrl' + '+'
                and in adobe acrobat pdf extension, 'ctrl' + 'shift' + '=' rotates the page.
                """

            case ["Encoder2", "RR", ["Mode"]]:
                logger.debug('Encoder2 rotate right with mode, reseting zoom')
                tools.perform_hotkey(['ctrl', '0'])  

            case ["Encoder2", "RLB", []]:
                logger.debug('Encoder2 rotate left w/ button, left arrow')
                tools.perform_press('left')

            case ["Encoder2", "RRB", []]:
                logger.debug('Encoder2 rotate right w/ button, right arrow')
                tools.perform_press('right')  

    def Button_handlerV3(self):
        #logger.debug("Button_handlerV2")

        focused_window = tools.get_focused()

        if focused_window is None:
            app = 'Desktop'
        else:
            split_focused_window = focused_window.split(" - ")
            split_focused_window.reverse()
            app = split_focused_window[0]


        match [app, self.button, self.mode, self.layers]:
            #Format: 
            #case [AppName, "ButtonNumber", "MacroMode"]:
            # Leave AppName _ for any app
            # MacroMode as mode for any mode
            # Layers is a list of layers where "Mode" will be the last one
            
            # Any app and Any Mode    And that are prioritives 
            case [_, 1, mode, []]:    # Shows what each button is defined as
                logger.debug("ButtonMode")
                threading.Thread(target = tools.ButtonMode, args=(mode, )).start()   

            case [_, 1, mode, [3]]:
                logger.debug("Moves currently foccused to the virtual Desktop on the left")
                tools.moveAppAccrossDesktops(app, 'Left')
                
            case [_, 1, mode, [4]]: 
                logger.debug("Moves currently foccused to the virtual Desktop on the right")
                tools.moveAppAccrossDesktops(app, 'Right')    
                    
            case [_, 2, mode, []]: # any app, any more and no layers
                logger.debug("Btn 2, no layers")
                tools.mediaTimerV2("Spotify")

            case [_, 2, mode, [1]]: # any app, any more and btn 1 as layer
                logger.debug("Btn 2, btn 1 as layer")
                tools.mediaTimerV2("Chrome")
            
            case [_, 2, mode, ['Mode']]: # any app, any more and btn 1 as layer
                logger.debug("Like")
                tools.spotifyControl("Like")
                #tools.mediaTimerV1("Chrome")

            case [_, 2, mode, [3, 4]]: # any app, any more and btn 1 as layer
                logger.debug("Moves Spotify to the current virtual Desktop")
                tools.moveSpotifyAccrossDesktops('Spotify Premium',  'Current')
                    
            case [_, 2, mode, [3]]:
                logger.debug("Moves Spotify to the virtual Desktop on the left")
                tools.moveSpotifyAccrossDesktops('Spotify Premium',  'Left')
            
            case [_, 2, mode, [4]]: 
                logger.debug("Moves Spotify to the virtual Desktop on the right")
                tools.moveSpotifyAccrossDesktops('Spotify Premium',  'Right')
            
            case [_, 3, mode, []]:    # move desktop left for any app
                threading.Thread(target = tools.change_desktop, args=('left', app)).start()

            case [_, 4, mode, []]:     # move desktop right for any app   
                threading.Thread(target = tools.change_desktop, args=('right', app)).start()
            



            case [_, 12, mode, []]:     # Pause button press
                logger.debug("Pause button press")
                self.change_pause_state()

                #main.on_clicked(None, lambda item: True)

            

            # TEST
            case ["Destiny 2", 5, mode, []]: # Rocket Flying Test
                #left clicks, then presses q, then moves mouse down 15 pixels
                logger.debug("Rocket Flying Test")
                tools.rocket_flying()

            case ["Destiny 2", 6, mode, []]: # Wellskate Test
                tools.wellskate()


            # Specific app and Any Mode
            # VS Code Layer
            case ["Visual Studio Code", 5, mode, []]: # run code in Vs code
                logger.debug("run code in Vs code")
                tools.perform_hotkey(['ctrl', 'alt', 'n'])

            # Star Citizen Layer
            case ["Star Citizen", 5, mode, []]: # focus front shields
                tools.sheild_focus_star_citizen("1")

            case ["Star Citizen", 6, mode, []]: # focus back shields
                tools.sheild_focus_star_citizen("2")

            case ["Star Citizen", 7, mode, []]: # Reset shields
                tools.sheild_focus_star_citizen("3")


            # # Any App, Specific Mode
            # case [_, 5, "2"]:     # Cut (Ctrl + x)
            #     logger.debug("Audacity Cut (Ctrl + x)")
            #     tools.perform_hotkey(['ctrl', 'x'])

            # case [_, 6, "2"]:     # Audacity Split Ctrl + i 
            #     logger.debug("Audacity Split (ctrl + i)")
            #     tools.perform_hotkey(['ctrl', 'i'])       

            # case [_, 9, "2"]:     # Backspace
            #     logger.debug("Backspace")               
            #     tools.perform_press(['backspace'])


            # Macros that are last priority.     
            case [_, 5, mode, []]:   # Text to speech
                logger.debug("Text to speech")
                tools.textToSpeech()
                #custom_keyboard.hotkey('ctrl', 'c')
                #threading.Thread(target = tools.Image_to_text2).start()
                
            case [_, 6, mode, []]:   # Stop Speech
                logger.debug("Stop Speech")
                tools.stopSpeech()
                #threading.Thread(target = tools.Image_to_text2).start()

            case [_, 7, mode, []]:   # Copy
                #logger.debug("Copy")
                #NOTE : this can cause a keyboard interupt if used in terminal
                tools.perform_hotkey(['ctrl', 'c'])             

            case [_, 8, mode, []]:   # Paste 
                #logger.debug("Paste")
                tools.perform_hotkey(['ctrl', 'v'])

            case [_, 9, mode, []]:   # Search highlighted text
                #logger.debug("Search highlighted text")
                tools.search_highlighted_text()

            case [_, 10, mode, []]:     # runs Task Manager      is button 10
                logger.debug("Starting Task manager")
                tools.perform_hotkey(['ctrl', 'shift', 'esc'])

            case [_, 11, mode, []]:   #image to text             is button 11
                logger.debug("Image to text")
                threading.Thread(target = tools.Image_to_text2).start()
        
    def Event_handler(self):
        logger.info(f"{self.button, self.event_type, self.layers}")

        if self.button in ["Encoder1", "Encoder2"]:
            self.Encoder_handler()
        
        else:
            self.Button_handlerV3()