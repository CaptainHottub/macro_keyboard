from logger import logger, toaster
import tools
import serial.tools.list_ports
import threading
import time

class MacroDriver:
    def __init__(self, baud_rate = 9600, mode = 1):
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
        
        def btn_renamer(btn):
            if btn in {0, 14, 15}:
                btn_names = {
                    0: "Mode",
                    14: "Encoder1",
                    15: "Encoder2"}
                btn = btn_names[btn]
            return btn

        events = {
            "0000": "btnPress",
            "0001": "btnRelease",
            "0010": "RL",   #rotary left w/o button
            "0011": "RR",   #rotary right w/o button
            "0110": "RLB",  #rotary left w/ button
            "0111": "RRB"   #rotary right w/ button
        }

        #print(msg)
        # splits the string every 4th character
        x = [msg[i:i+4] for i in range(0, len(msg), 4)]
        x.reverse()

        btn_num = int(x[0],2)  # converst the binary string into and integer

        # renames buttons 0, 14 and 15 to Mode, Encoder1 and Encoder2    
        btn_num = btn_renamer(btn_num)

        event_type = events[x[1]]

        # layers = [ btn_renamer(int(i,2))  for i in x[2:]  if len(x) > 2 ]
        
        layers = []
        if len(x) > 2:
            for i in x[2:] :
                layers.append(btn_renamer(int(i,2)))

        #print(btn_num, event_type, layers)
        return btn_num, event_type, layers
    

    # I want to rewrite this so it looks better
    def start(self):
        while self.run:
            if self.serial_port is None:    # If the serial port is not connected/not defined
                # Look for the device

                arduino_ports = [
                    p.device for p in serial.tools.list_ports.comports()
                    #if 'Arduino Micro' in p.description
                    if 'USB Serial Device' in p.description
                ]

                #arduino_ports=["COM3"]
            
                if not arduino_ports:
                    logger.info('No Arduino Micro found in comports. Retrying in 5 seconds...')
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
                    if self.pause_state == False: # Buttons wont be ignored
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

                except ValueError:
                    logger.error('ValueError, stop() has been called, goodbye...')

                except Exception as exception:
                    logger.warning(f'Exception raised: {exception = }')
                    #logger.error('ValueError, stop() has been called, goodbye...')

        logger.error('PROGRAM is shutting down')
    

    def Encoder_handler(self):
        #print(self.button, self.event_type, self.layers)

        match [self.button, self.event_type, self.layers]:

            case ["Encoder1", "RL", []]:
                logger.debug('VolumeDown')
                tools.spotifyControlTest("VolumeDown")
            
            case ["Encoder1", "RR", []]:
                logger.debug('VolumeUp')
                tools.spotifyControlTest("VolumeUp")
            
            case ["Encoder1", "RLB", []]:
                logger.debug('Back5s')
                tools.spotifyControlTest("Back5s")
            
            case ["Encoder1", "RRB", []]:
                logger.debug('Forward5s')
                tools.spotifyControlTest("Forward5s")

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

            # case ["Encoder2", "RLB", []]:
            #     logger.debug('"Encoder2", "RLB", []')
            
            case ["Encoder2", "RRB", []]:
                logger.debug('Encoder2 rotate right with button, reseting zoom')
                tools.perform_hotkey(['ctrl', '0'])

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