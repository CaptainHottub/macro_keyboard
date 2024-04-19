from logger import logger, toaster
import tools
import serial.tools.list_ports
import threading
import time
import easylogger

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
        
        self.btn_names = {
            0: "Mode",
            14: "Encoder1",
            15: "Encoder2"}
        
        self.event_names = {
            "0000": "btnPress",
            "0001": "btnRelease",
            "0010": "RL",   #rotary left w/o button
            "0011": "RR",   #rotary right w/o button
            "0110": "RLB",  #rotary left w/ button
            "0111": "RRB"   #rotary right w/ button
            }
        
        self.held_keys_timestamp = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
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

    def connect(self, deviceName: str):
        """
        This tries to "connect" to the device with the specified name.  
        
        Pass the name of the device you want to connect to as a arg.
        
        Will return True if successfull, will return False if not, and will stop the program if something is already connected to it.

        When return is True, you can use self.serial_port to interact with the device
        """
        logger.debug("in connect")

        # returns the comport of the device with the name/FriendlyName of 'Pi Pico Macro Driver'
        ## I used this video to change the name of my Pi Pico from USB Serial Device to 'Pi Pico Macro Driver':  https://youtu.be/KZ3Gw_u-Rl0?si=Xwfqxc1omLGeiCem&t=120
        port = [p.device for p in serial.tools.list_ports.comports()
                if deviceName in p.description]
  
        try:
            self.com_port = port[0]

            self.serial_port = serial.Serial(self.com_port, self.baud_rate)
            logger.info(f'Connected to serial port {self.com_port} at {self.baud_rate} baud')
            toaster.show_toast("Connected","Connected to Pi Pico succesfully!", duration=2, threaded=True)

        except serial.serialutil.SerialException:
            logger.critical('Pi Pico is already connected to something, shutingdown')
            toaster.show_toast("Access is denied","Pi Pico is already connected to something", duration=2, threaded=True)
            self.stop()
        except IndexError as e:
            logger.error(f'IndexError: {e}')
            logger.error('Will wait for 2 sec then try again.')
            time.sleep(2)

        except Exception as e:
            logger.error(f'Error connecting to serial port {self.com_port}: {e}')
            return False

        else:
            return True

    def timestamper(self, event_num, event_type):
        
        ### timstamp stuff
        if event_type == 'btnPress':  #  if the event_type is a button press
            self.held_keys_timestamp[event_num] = time.time_ns()
            
            #logger.debug('Event was a press')
            
            return False

        elif event_type == 'btnRelease':
            timestamp = self.held_keys_timestamp[event_num]
            diff_ns = time.time_ns() - timestamp
            diff_ms = diff_ns /1000000
            
            #logger.debug(f'time held for {event_num=} is {diff_ms=}')
            
            self.held_keys_timestamp[event_num] = 0
            if diff_ms > 150:    
                #logger.debug('button was held for more then 150 ms, returning')
                return False
        
        return True
       
    def msg_parser(self, msg):
        #logger.debug(f'{msg=}')

       # splits the string every 4th character
        split_msg = [msg[i:i+4] for i in range(0, len(msg), 4)]
        event_type_bits, event_name_bits = split_msg
        #logger.debug(f'{event_type_bits=}, {event_name_bits=}')

        event_type = self.event_names[event_type_bits]
        #logger.debug(f'{event_type=}')

        # converts the binary string into and integer
        event_num = int(event_name_bits,2) 
        
        result = self.timestamper(event_num, event_type)
        #logger.debug(f'{result=}')
  
        if result:
            event_name = self.btn_names[event_num] if event_num in [0, 14, 15] else event_num
            return event_name, event_type
        else:
            return False

    def count_layers(self) -> list:
        layers = []

        if self.held_keys_timestamp.count(0) < len(self.held_keys_timestamp):#
            
            logger.debug("there should be layers")
            
            for index, value in enumerate(self.held_keys_timestamp, 0):
                if value != 0:
                    diff_ns = time.time_ns() - value
                    diff_ms = diff_ns /1000000

                    if diff_ms > 150:
                        
                        logger.debug(f'time held for {index=} is {diff_ms=}')
                        
                        if index == 0:
                            layers.append('Mode')
                        else:    
                            layers.append(index)
        
        return layers
            
    def Event_Parser(self, msg):
        """
        self.button = event_name

        self.event_type = event_type

        self.layers = layers
        
        """
        logger.debug('in eventHandler')
    
        event = self.msg_parser(msg)
        if not event:
            logger.debug('Event as a button press, or was held for too long.')
            return False
        
        logger.debug('Event is a button release')
        event_name, event_type = event

        layers = self.count_layers()

        #logger.info(f'{event_name=}, {event_type=}, {temp_layers=}')

        self.button = event_name
        self.event_type = event_type
        self.layers = layers
        return True
    
    def Driver(self):
        while self.run:
            if not self.serial_port:
                #### there is no serial port, so  we are not connected
                self.connect('Pi Pico Macro Driver')
                # IDK what to make it do if it returns 0
            else:
                #logger.debug("in else")
                #time.sleep(0.2)
                
                try:
                    received_string = str(self.serial_port.readline(), 'utf-8').strip()

                    if self.Event_Parser(received_string):
                        #print(received_string)
                        if self.button == "Mode":
                            self.update_mode()
                            continue
                        
                        # if pause_state is True, buttons will be ignored, except for B, it toggles pause_state
                        if self.pause_state == False: # Buttons wont be ignored
                            #self.Button_handlerV3(btn, event_type, layers)
                            #self.Event_handler(btn, event_type, layers)

                            if self.button in ['Encoder1', 'Encoder2']:
                                self.Encoder_handler()
                            else:
                                self.Button_handlerV3()

                        elif self.button == 12:
                            logger.debug('button 12 was pressed and pause state is true')
                            self.change_pause_state()
                        else:
                            logger.info('pause_state was set to True, ignoring button press')


                except serial.serialutil.SerialException:
                    logger.error(f'Pi Pico disconnected from {self.com_port}. Looking for device...')

                    toaster.show_toast("Arduino Micro disconnected", 
                                       f'Arduino Micro disconnected from {self.com_port}. Looking for device...', 
                                       duration=2, 
                                       threaded=True)

                    self.serial_port = None
                    # this is here so it doesn't throw 5 FileNotFoundError exception
                    time.sleep(0.2) 
                    continue

                except ValueError as  e:
                    logger.error(f'ValueError: {e}')

                    #logger.error('ValueError, stop() has been called, goodbye...')

                except Exception as exception:
                    logger.warning(f'Exception raised: {exception = }')
                    #logger.error('ValueError, stop() has been called, goodbye...')

        logger.critical('PROGRAM is shutting down')


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
            # Layers is a list of layers, where mode will be first and they will be in order
            
            # Any app and Any Mode    And that are prioritives 
            case [_, 1, mode, []]:    # Shows what each button is defined as
                logger.debug("ButtonMode")
                twrv = threading.Thread(target = tools.ButtonMode, args=(mode, )).start()   

            case [_, 2, mode, []]: # any app, any more and no layers
                logger.debug("Btn 2, no layers")
                tools.mediaTimerV1("Spotify")

            case [_, 2, mode, [1]]: # any app, any more and btn 1 as layer
                logger.debug("Btn 2, btn 1 as layer")
                tools.mediaTimerV1("Chrome")
            
            case [_, 2, mode, ['Mode']]: # any app, any more and btn 1 as layer
                logger.debug("Like")
                tools.spotifyControlTest("Like")
                #tools.mediaTimerV1("Chrome")

            case [_, 2, mode, [3, 4]]: # any app, any more and btn 1 as layer
                logger.debug("Moves Spotify to the current virtual Desktop")
                tools.MoveSpotifyToCurrentDesktop()

            case [_, 3, mode, []]:    # move desktop left for any app
                twrv = threading.Thread(target = tools.change_desktop, args=('left', app)).start()

            case [_, 4, mode, []]:     # move desktop right for any app   
                twrv = threading.Thread(target = tools.change_desktop, args=('right', app)).start()
            



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
                #logger.debug("Text to speech")
                #custom_keyboard.hotkey('ctrl', 'c')
                twrv = threading.Thread(target = tools.textToSpeech, args=()).start()

            case [_, 6, mode, []]:   # Stop Speech
                #logger.debug("Stop Speech")
                twrv = threading.Thread(target = tools.stopSpeech, args=()).start()

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
                twrv = threading.Thread(target = tools.Image_to_text2).start()
        
    def Event_handler(self):
        logger.info(f"{self.button, self.event_type, self.layers}")

        if self.button in ["Encoder1", "Encoder2"]:
            self.Encoder_handler()
        
        else:
            self.Button_handlerV3()