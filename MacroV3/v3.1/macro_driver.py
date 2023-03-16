from logger import logger
import tools
import serial.tools.list_ports
import threading
import time
from win10toast import ToastNotifier

toaster = ToastNotifier()
NOTIFICATION = {
    "ShowNotification": True,
    "Duration": 1.5
    }


class MacroDriver:
    def __init__(self, baud_rate = 9600):
        self.baud_rate = baud_rate
        self.serial_port = None
        self.run = True

    def stop(self):
        self.run = False 
        if self.serial_port:
            self.serial_port.close()

    def start(self):
        while self.run:
            if self.serial_port is None:
                # Look for the device
                arduino_ports = [
                    p.device for p in serial.tools.list_ports.comports()
                    if 'Arduino Micro' in p.description
                ]
                if not arduino_ports:
                    logger.info('No Arduino Micro found in comports. Retrying in 5 seconds...')
                    time.sleep(5)
                    continue
               
                # Connect to the first available device
                self.com_port = arduino_ports[0]

                try:
                    self.serial_port = serial.Serial(self.com_port, self.baud_rate)
                    logger.info(f'Connected to serial port {self.com_port} at {self.baud_rate} baud')
                    toaster.show_toast("Connected","Connected to Arduino succesfully!", icon_path=None, duration=NOTIFICATION["Duration"], threaded=True)

                except serial.serialutil.SerialException:
                    logger.critical('Arduino is already connected to something, shutingdown')
                    toaster.show_toast("Access is denied","Arduino is already connected to something", icon_path=None, duration=NOTIFICATION["Duration"], threaded=True)
                    self.stop()

                except Exception as e:
                    logger.error(f'Error connecting to serial port {self.com_port}: {e}')
                    continue

            else:

                try:
                    button_string = str(self.serial_port.readline(), 'utf-8').strip()

                    if 'mode button was pressed' in button_string:
                        logger.info(button_string)
                        continue

                    #logger.debug(f'Received button event: {button_string}')
                    button_string = button_string[-3:]
                    button, macro_mode = button_string.split(".")

                    # Call Button_handler() with button_string as an argument
                    #self.Button_handler(button, macro_mode)
                    self.Button_handlerV2(button, macro_mode)

                except serial.serialutil.SerialException:
                    logger.error(f'Arduino Micro disconnected from {self.com_port}. Looking for device...')
                    
                    toaster.show_toast("Arduino Micro disconnected", 
                                       f'Arduino Micro disconnected from {self.com_port}. Looking for device...', 
                                       icon_path=None, 
                                       duration=NOTIFICATION["Duration"], 
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
    

    def Button_handlerV2(self, buttonNumber, macroMode):
        #logger.debug("Button_handlerV2")

        focused_window = tools.get_focused()

        if focused_window is None:
            app = 'Desktop'

        else:
            split_focused_window = focused_window.split(" - ")
            split_focused_window.reverse()
            app = split_focused_window[0]

        # logger.debug(f"Focused app is {app}")
        # logger.debug(f'{buttonNumber = } and {macroMode = }')

        # Match case for buttons.
        match [app, buttonNumber, macroMode]:
            #Format: 
            #case [AppName, "ButtonNumber", "MacroMode"]:
            # Leave AppName _ for any app
            # MacroMode as mode for any mode

            # Any app and Any Mode    And that are prioritives 
            case [_, "1", mode]:    # Shows what each button is defined as
                logger.debug("ButtonMode")
                twrv = threading.Thread(target = tools.ButtonMode, args=(mode, )).start()

            case [_, "2", mode]:    # pause song spotify for any app
                logger.debug("pause song spotify \n")
                tools.spotifyV3()

            case [_, "3", mode]:    # move desktop left for any app
                twrv = threading.Thread(target = tools.change_desktop, args=('left', app)).start()

            case [_, "4", mode]:     # move desktop right for any app   
                twrv = threading.Thread(target = tools.change_desktop, args=('right', app)).start()


            # Specific app but any Mode
            # VS Code Layer
            case ["Visual Studio Code", "5", mode]: # run code in Vs code
                logger.debug("run code in Vs code")
                tools.perform_hotkey(['ctrl', 'alt', 'n'])

            # Star Citizen Layer
            case ["Star Citizen", "5", mode]: # focus front shields
                tools.sheild_focus_star_citizen("1")

            case ["Star Citizen", "6", mode]: # focus back shields
                tools.sheild_focus_star_citizen("2")

            case ["Star Citizen", "7", mode]: # Reset shields
                tools.sheild_focus_star_citizen("3")


            # TEST
            case ["Destiny 2", "5", mode]: # Rocket Flying Test
                #left clicks, then presses q, then moves mouse down 15 pixels
                logger.debug("Rocket Flying Test")
                tools.rocket_flying()


            # Any App, Specific Mode
            case [_, "5", "2"]:     # Cut (Ctrl + x)
                logger.debug("Audacity Cut (Ctrl + x)")
                tools.perform_hotkey(['ctrl', 'x'])

            case [_, "6", "2"]:     # Audacity Split Ctrl + i 
                logger.debug("Audacity Split (ctrl + i)")
                tools.perform_hotkey(['ctrl', 'i'])       

            case [_, "9", "2"]:     # Backspace
                logger.debug("Backspace")               
                tools.perform_press(['backspace'])


            # Macros that are last priority.     
            case [_, "5", mode]:   # Text to speech
                logger.debug("Text to speech")
                #custom_keyboard.hotkey('ctrl', 'c')
                twrv = threading.Thread(target = tools.textToSpeech, args=()).start()

            case [_, "6", mode]:   # Stop Speech
                logger.debug("Stop Speech")
                twrv = threading.Thread(target = tools.stopSpeech, args=()).start()

            case [_, "7", mode]:   # Copy
                logger.debug("Copy")
                #NOTE : this can cause a keyboard interupt if used in terminal
                tools.perform_hotkey(['ctrl', 'c'])             

            case [_, "8", mode]:   # Paste 
                logger.debug("Paste")
                tools.perform_hotkey(['ctrl', 'v'])

            case [_, "0", mode]:     # runs Task Manager      is button 10
                logger.debug("Starting Task manager")
                tools.perform_hotkey(['ctrl', 'shift', 'esc'])

            case [_, "A", mode]:   #image to text             is button 11
                logger.debug("Image to text")
                twrv = threading.Thread(target = tools.Image_to_text2).start()
    
