from funcs import *
from infi.systray import SysTrayIcon
import serial.tools.list_ports
import sys

import ctypes_keyboard
import custom_keyboard

# test
icon_path = "C:\Coding\Arduino Stuff\Projects\Arduino Python\MacroV2\python.ico"
#https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread-in-python

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter_ns()
        func(*args, **kwargs)
        print(f"Function took: {(time.perf_counter_ns() - start)/1000000} milliseconds")
    return wrapper


stats = {
    "mouse_pos" : None,
    "focused_app": None,
    "is_fullscreen": None,
    "app_hwnd": None}
def get_stats(loop=False, m=False, f=True, interval=2):
    """
    Parameters
    ----------
    loop : bool
        True of False. [default: False]
        Will make it loop if true
    m  : bool
        True of False. [default: False]
        Gets the mouse position
    w  : bool
        True of False. [default: True]
        Gets what is focused and if it is fullscreen
    interval : int or float.
        update interval [default: 0.2] seconds.
    """
    def mouse():
        stats["mouse_pos"] = pyautogui.position()
    
    def focus():
        hWnd = user32.GetForegroundWindow()
        stats["app_hwnd"] = hWnd
        
        name = win32gui.GetWindowText(hWnd)
        name = name.split(" - ")
        name.reverse()
        stats["focused_app"] = name

        try:
            rect = win32gui.GetWindowRect(hWnd)
            if 'Google Chrome' in win32gui.GetWindowText(hWnd): # if youtube or google chrome is in the name of the window.
                fullscreen = False
            fullscreen = rect == full_screen_rect
            
        except Exception:
            fullscreen = False
        stats["is_fullscreen"] = fullscreen

    if loop:
        while True:
            time.sleep(interval)
            if m:
                mouse()
            if f:
                focus()
    if m:
        mouse()
    if f:
        focus()

#@timer
def Button_handler(button):
    get_stats()

    app = stats["focused_app"][0]
    match [app, button.split()]:

        case [_, ("2", mode)]: # pause song spotify for any app
            log.debug("pause song spotify")
            spotify()

        case [_, ("3", mode)]:    # move desktop left for any app
            log.debug("move desktop left")
            twrv = Thread(target = Change_desktop, args=('left',)).start()

        case [_, ("4", mode)]:     # move desktop right for any app   
            log.debug("move desktop Right")
            twrv = Thread(target = Change_desktop, args=('right',)).start()

        # any specific layers

        case ["Star Citizen", ("5", mode)]: # focus front shields
            log.debug("right shift + 1")

            custom_keyboard.hotkey('shiftright', '1')

            # ctypes_keyboard.PressKey(0xa1)  #right shift
            # ctypes_keyboard.PressKey(0x31) # 1
            # time.sleep(0.1)
            # ctypes_keyboard.ReleaseKey(0xa1)#right shift
            # ctypes_keyboard.ReleaseKey(0x31)# 1

        case ["Star Citizen", ("6", mode)]: # focus back shields
            log.debug("right shift + 2")

            custom_keyboard.hotkey('shiftright', '2')

            # ctypes_keyboard.PressKey(0xa1)  #right shift
            # ctypes_keyboard.PressKey(0x32) # 2
            # time.sleep(0.1)
            # ctypes_keyboard.ReleaseKey(0xa1)#right shift
            # ctypes_keyboard.ReleaseKey(0x32)# 2

        case ["Star Citizen", ("7", mode)]: # Reset shields
            log.debug("right shift + 3")

            custom_keyboard.hotkey('shiftright', '3')

            # ctypes_keyboard.PressKey(0xa1)  #right shift
            # ctypes_keyboard.PressKey(0x33) # 3
            # time.sleep(0.1)
            # ctypes_keyboard.ReleaseKey(0xa1)#right shift
            # ctypes_keyboard.ReleaseKey(0x33)# 3


        # any other button that is not defined / default
        # case [_, (btn, mode)]:
        #     print(f"button {btn} pressed on {app}")

        case [_, ("5", mode)]:
            log.debug("button 5 ")
            #pyautogui.hotkey('shiftright','1')

            # ctypes_keyboard.keyTest('ctrl')

            # ctypes_keyboard.keyTest('alt', 'tab')
            # Works
            # ctypes_keyboard.PressKey(0xa1)  #right shift
            # ctypes_keyboard.PressKey(0x31) # 1
            # time.sleep(0.1)
            # ctypes_keyboard.ReleaseKey(0xa1)#right shift
            # ctypes_keyboard.ReleaseKey(0x31)# 1
            #ctypes_keyboard.HotKey('num5', 'num8', 'num2')

    
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
    DEBUG = 1  # 0 for off 1 for DEBUG logs on
    logger_setup(DEBUG)
    from funcs import log

    main()