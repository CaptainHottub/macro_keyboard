import time
from infi.systray import SysTrayIcon
import serial.tools.list_ports
import pyautogui
from threading import Thread
import funcs
import sys
#import timeit
from argparse import ArgumentParser

# Open in powershell
# cd 'C:\Coding\Arduino Stuff\Projects\Arduino Python\MacroV2\'
# python .\MacroV2.py --d 1

# C:\Python310\python.exe "C:\Coding\Arduino Stuff\Projects\Arduino Python\MacroV2\MacroV2.py" --d 1
parser = ArgumentParser(description='Enable debug mode')
parser.add_argument('--d',type=int, help='Enable debug mode')
args = parser.parse_args()
DEBUG = args.d
if DEBUG is None:
    DEBUG=0

# OVERIDE
#DEBUG=1

icon_path = "C:\Coding\Python\pythonScript.ico"
#https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread-in-python


#DEBUG = 0  # 0 for off 1 for DEBUG logs on, 2 for process progress bars
funcs.logger_setup(DEBUG)
from funcs import log

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter_ns()
        func(*args, **kwargs)
        print(f"Function took: {(time.perf_counter_ns() - start)/1000000} milliseconds")
    return wrapper


#@timer
def Button_handler(button):

    match button.split():

        ###### Macros that work for all modes
        case ["1", ("1" | "2" | "3" | "4") as mode]:    
            log.debug("ButtonMode")
            twrv = Thread(target= funcs.ButtonMode, args=(mode, )).start()

        case ["3", ("1" | "2" | "3" | "4") as mode]:    # move desktop left
            log.debug("move desktop left")
            twrv = Thread(target=funcs.Change_desktop, args=('left',)).start()

        case ["4", ("1" | "2" | "3" | "4") as mode]:     # move desktop right   
            log.debug("move desktop Right")
            twrv = Thread(target=funcs.Change_desktop, args=('right',)).start()

        case ["9", ("1" | "2" | "3" | "4") as mode]:   # Copy
            log.debug("Copy")
            #NOTE : this can cause a keyboard interupt if used in terminal
            pyautogui.hotkey('ctrl', 'c')

        case ["0", ("1" | "2" | "3" | "4") as mode]:   # Paste 
            log.debug("Paste")
            pyautogui.hotkey('ctrl', 'v') 

        case ["A", ("1" | "2" | "3" | "4") as mode]:   #image to text
            log.debug("Image to text")
            twrv = Thread(target=funcs.Image_to_text).start()


        ###### Macros for specific modes
        #   button, mode

        # Why not just connect once on first play pause. then have a daemon thread thats just connected, and pass commands to it instead of using pyautogui
        # it can be a class with functions in it.
        case ["2", "1"]: # pause song spotify
            log.debug("pause song spotify")
            funcs.spotify()

        # case ["7", "1"]:    # Volume Up   CTRL up arrow, for spotify
        #     log.debug("Volume Up")
        #     pyautogui.hotkey('volumeup')  

        # case ["8", "1"]:    # Volume Down   CTRL down arrow, for spotify
        #     log.debug(" Volume Down")
        #     pyautogui.hotkey('volumedown')  


        ### MODE 2
        case ["7", "2"]:
            pyautogui.hotkey('alt', 'i') 
            time.sleep(0.1)
            pyautogui.press('e') 
        case ["8", "2"]:
            funcs.input_special_char()


        case _:
            print("there is no macro for that button")

def on_quit(systray):
    """
    Quits the program,
    ser.close() raises a index out of range error, 2 NoneType errors 
    then finally a serial.serialutil.PortNotOpenError execption
    which we catch in the main try. once we catch it wan can do sys.exit(1) 
    """
    log.critical("PROGRAM is shutting down")
    SysTrayIcon.shutdown
    ser.close()
   
 
def Connect():
    """
    Tries to connect to the arduino.  Outputs None if it cant connect.
    """
    log.info("Connecting to Arduino...")

    log.info("Getting port")
    ports = serial.tools.list_ports.comports()
    log.debug(f"{ports=}")

    # gets the port the arduino is connected to, returns [ ], if there is no arduino port
    arduinoPort = [port for port, desc, hwid in sorted(ports) if "Arduino Micro" in desc]
    log.info("Got arduino port"), log.debug(f"{arduinoPort=}")

    try: 
        ser = serial.Serial(arduinoPort[0], 9600)
    except serial.serialutil.SerialException:
        log.warning("Arduino is already connected to something")
        sys.exit(1)

    else:
        log.info("Connected to Arduino")
        return ser

def setup(type=None):
    while True:
        if type is not None: # this used when trying to reconect to arduino
            time.sleep(type)

        try:
            global ser
            ser = Connect()
            if DEBUG ==2:
                monitor = Thread(target=funcs.cpu_ram_monitor, daemon=True).start()

        except Exception as e:
            log.error(e)
        else:
            log.info("Setup was a success")
            print()
            return ser


def main():
    systray = SysTrayIcon(icon_path, "Python Macro", on_quit=on_quit) # little icon in bottom right
    systray.start()

    ## setup
    global ser
    ser = setup()
    
    while True:
        try: 
            cc = str(ser.readline())
            if 'mode button was pressed' in cc:
                log.info(cc)
                continue

            global button
            button = (f"{cc[9]} {cc[11]}")

            Button_handler(button)

        except serial.serialutil.PortNotOpenError:
            log.critical("Program quiting, goodbye")
            sys.exit(1) 

        except Exception as e:
            log.warning(e)
            print()

            if type(e) is serial.SerialException:
                log.warning("Arduino disconected, trying to reconect")
                print()
                ser = None
                setup(3)
                
if __name__ == "__main__":
    main()