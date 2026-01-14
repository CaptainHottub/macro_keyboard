#device.py
# will contain the class, and code needed to interact witht the keyboard
import serial
import serial.tools.list_ports
import time
import json
import platform
import sys

from logger_setup import get_logger, setup_logging
from notifications import send_notification
from config import settings
import macros
from macro_handlers import encoder_handler, button_handler  # Import the new functions

setup_logging()
logger = get_logger("DeviceDriver")

class MacroDriver:
    """
    Manages communication with the KB2040 device for macro operations.
    """
    def __init__(self):
        self.baud_rate = settings.get('device.baud_rate', 115200)
        self.device_name = settings.get('device.name', "KB2040 - CircuitPython")
        self.run = True
        self.mode = 1
        self.serial_port = None
        self.port_name = None
        self.sys_name = platform.system().lower()
        # self._recursion_count = 0
        # self._max_recursion = 10

    def update_mode(self):
        self.mode += 1
        if self.mode > 2:
            self.mode = 1
        logger.info(f'Mode is now {self.mode}')


    def stop(self):
        self.run = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            logger.info("Serial port closed.")

    def _find_device_port(self):
        ports = [port.device for port in serial.tools.list_ports.comports()
                 if self.device_name in port.description]
        return ports[0] if ports else None
    
    def connect_serial(self):
        if self.serial_port and self.serial_port.is_open:
            return True

        if not self.port_name:
            self.port_name = self._find_device_port()
            if not self.port_name:
                logger.info(f'No {self.device_name} found. Retrying...')
                return False
        
        try:
            self.serial_port = serial.Serial(self.port_name, self.baud_rate, timeout=0.05)
            logger.info(f'Connected to serial port {self.port_name} at {self.baud_rate} baud')
            send_notification(title='Connected', msg=f'Connected to {self.device_name} successfully!')
            return True
        except serial.serialutil.SerialException as e:
            logger.critical(f'Serial connection failed: {e}. Another program may be using the port.')
            send_notification(title='Access Denied', msg='Access denied. Another application may be using the port.', urgency='critical')
            self.run = False
            return False
        except Exception as e:
            logger.error(f'Unexpected error during serial connection: {e}')
            self.port_name = None
            return False

    def write_serial(self, data):
        """
        Writes JSON data to the serial port, handling connection issues.
        """
        if not self.serial_port or not self.serial_port.is_open:
            logger.warning("Attempted to write to a closed or nonexistent serial port. Attempting to reconnect.")
            if not self.connect_serial():
                logger.error("Could not write data, reconnection failed.")
                return

        try:
            message = (json.dumps(data) + '\n').encode('utf-8')
            self.serial_port.write(message)
        except Exception as e:
            logger.error(f"Failed to write to serial port: {e}")
            self._handle_serial_error()

    def _handle_serial_error(self):
        logger.error("Exception on read. Board likely disconnected.")
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.serial_port = None
        self.port_name = None
        logger.info("Connection to microcontroller closed. Will attempt reconnect.")

    def read_loop(self):
        """Main loop for reading from the serial port."""
        while self.run:
            if not self.connect_serial():
                time.sleep(5)
                continue
            
            try:
                line = self.serial_port.readline()
                
                if line:
                    
                    try:
                        data = json.loads(line.decode("utf8").strip())
                        
                        if "raw" in data:
                            logger.debug(f"Raw data: {data['raw']}")
                            return
                        # if data.get('Button_id') == 'Mode':
                        #     self.update_mode()
                        #     return
                        
                        self.event_handler(data, self.mode)
                        
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to decode JSON: {line.decode('utf8').strip()}")
                        logger.debug(f"Raw line data: {line}")
                        
                    except Exception as e:
                        logger.error(f"Error processing received data: {e}")

            except serial.SerialException as e:
                logger.error(f"SerialException in read_loop: {e}")
                self._handle_serial_error()
                time.sleep(1)
            except KeyboardInterrupt:
                logger.critical("KeyboardInterrupt - quitting")
                self.stop()
                sys.exit()
            except Exception as e:
                logger.error(f"Unexpected error in read_loop: {e}")
                self._handle_serial_error()
                time.sleep(1)

    
    def event_handler(self, event_data, mode):
        """Handles incoming events and executes platform-specific macros."""
        logger.info(f"Event: {event_data}, Mode: {mode}")

        app_data = {}
        
        # bunch of giberish to determine the focused app. is none, it returns "Desktop"
        if self.sys_name == 'linux':
            focused_window_data = macros.get_focused_window_info()            
            if focused_window_data:
                window_title = focused_window_data.get('name', '')
                separators = [' - ', ' — ']
                for sep in separators:
                    if sep in window_title:
                        window_title = window_title.split(sep)[-1]
                        break
                else:
                    if focused_window_data.get('class', '').lower() in window_title.lower():
                        window_title = focused_window_data['class']
                    elif "desktop" in window_title.lower():
                        window_title = 'Desktop'
                
                tmp_hwnd= focused_window_data.get('id')
            
            else:
                window_title = "desktop"
                tmp_hwnd='0'
                
            app_data = {"app": window_title, "hwnd": tmp_hwnd}
        
        elif self.sys_name == 'windows':
            focused_window_title, focused_window_hwnd = macros.get_focused_name()
            
            if not focused_window_title:
                app = 'Desktop'
            else:
                separators = [" - ", " — "]
                app_title = focused_window_title
                for sep in separators:
                    if sep in app_title:
                        app_title = app_title.split(sep)[-1]
                        break
                app = app_title.strip()
            
            app_data = {"app": app, "hwnd": focused_window_hwnd}
        
        else:
            logger.warning(f"Unsupported platform for window focus: {self.sys_name}")
            return
        
        logger.debug(app_data)
        
        # Makes everything in the layers list a string.
        # event_data['Layers'] = [str(item) for item in event_data.get('Layers', [])]

        # Dispatch events to appropriate handlers
        if 'Encoder' in event_data:
            encoder_handler(event_data, mode, app_data)
        elif 'ButtonId' in event_data:
            button_handler(event_data, mode, app_data, self)


    # def encoder_handler(self, event_data, mode, app_data):
    #     """Handles encoder events."""
    #     logger.info(f"Encoder event received: {event_data}")
    #     # Your specific encoder macro logic goes here

    # def button_handler(self, event_data, mode, app_data):
    #     """Handles button events."""
    #     logger.info(f"Button event received: {event_data}")
    #     # Your specific button macro logic goes here

    def change_rgb(self, pixels, color):
        """
        Sends a command to change the RGB color of specified pixels.
        work in progress...     not really
        """
        data = {"color": [pixels, color]}
        self.write_serial(data)

