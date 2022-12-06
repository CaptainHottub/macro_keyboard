from funcs import *
import pystray
from PIL import Image
import serial.tools.list_ports
import sys
import custom_keyboard
from ctypes_keyboard import PressKey, ReleaseKey
from win10toast import ToastNotifier

"""
TODO
in V2.3.1:
try and transition all pyautogui keyboard funtions to custom_keyboard
add a write function to custom_keyboard

have one dictionary that contains all Vk_codes
"""

image = Image.open("C:\Coding\Arduino Stuff\Projects\macro_keyboard\MacroV2\pythonIcon.ico") 
#https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread-in-python

toaster = ToastNotifier()
#hmm

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
        case ["Visual Studio Code", ("5", mode)]: # run code in Vs code
            pyautogui.hotkey('ctrl', 'alt', 'n') 

        case ["Star Citizen", ("5", mode)]: # focus front shields
            log.debug("right shift + 1")
            custom_keyboard.hotkey('shiftright', '1')
            time.sleep(0.1)
            custom_keyboard.press('shiftright')

            # PressKey(0xa1)  #right shift
            # PressKey(0x31) # 1
            # time.sleep(0.1)
            # ReleaseKey(0xa1)#right shift
            # ReleaseKey(0x31)# 1

        case ["Star Citizen", ("6", mode)]: # focus back shields
            log.debug("right shift + 2")
            custom_keyboard.hotkey('shiftright', '2')
            time.sleep(0.1)
            custom_keyboard.press('shiftright')

            # PressKey(0xa1)  #right shift
            # PressKey(0x32) # 2
            # time.sleep(0.1)
            # ReleaseKey(0xa1)#right shift
            # ReleaseKey(0x32)# 2

        case ["Star Citizen", ("7", mode)]: # Reset shields
            log.debug("right shift + 3")
            custom_keyboard.hotkey('shiftright', '3')
            time.sleep(0.1)
            custom_keyboard.press('shiftright')

            # PressKey(0xa1)  #right shift
            # PressKey(0x33) # 3
            # time.sleep(0.1)
            # ReleaseKey(0xa1)#right shift
            # ReleaseKey(0x33)# 3


        # any other button that is not defined / default
        case [_, ("1", mode)]:    
            log.debug("ButtonMode")
            twrv = Thread(target = ButtonMode, args=(mode, )).start()
            
        case [_, ("9", mode)]:   # Copy
            log.debug("Copy")
            #NOTE : this can cause a keyboard interupt if used in terminal
            custom_keyboard.hotkey('ctrl', 'c')

        case [_, ("0", mode)]:   # Paste 
            log.debug("Paste")
            custom_keyboard.hotkey('ctrl', 'v')

        case [_, ("A", mode)]:   #image to text
            # Press Win + Shift + s, 
            # wait for mouse release event with pynput then do Image_to_text
            log.debug("Image to text")
            twrv = Thread(target = Image_to_text).start()

        #case [_, (btn, mode)]:
        #    print(f"button {btn} pressed on universal layer")

def on_quit(type):
    """
    Quits the program,
    ser.close() raises a index out of range error, 2 NoneType errors 
    then finally a serial.serialutil.PortNotOpenError execption
    which we catch in the main try. once we catch it wan can do sys.exit(1) 
    """
    log.critical("PROGRAM is shutting down")
    systray.stop()
    if type == 1:
        ser.close()
    exit(1)
    #ser.close()


def setupV2(type=None):
    while True:
        if type is not None: # this used when trying to reconect to arduino
            time.sleep(type)

        try:
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
            global ser
            ser = serial.Serial(arduinoPort[0], 9600)

        except serial.serialutil.SerialException as err:
            log.error("Arduino is already connected to something, Access is denied.")
            toaster.show_toast("Access is denied","Arduino is already connected to something", icon_path=None, duration=3, threaded=True)
            on_quit(0)

        except Exception as e:
        
            log.error(e)
            time.sleep(0.2)
        else:
            log.info("Connected to Arduino")
            toaster.show_toast("Macro Keypad is connected", icon_path=None, duration=3, threaded=True)
            log.info("Setup was a success")
            print()

            return ser

def sysIcon():
    global systray
    systray = pystray.Icon(name="Python Macro", icon=image, title="Python Macro", menu=pystray.Menu(
        #pystray.MenuItem("Quit", on_quit)
        pystray.MenuItem("Quit", lambda: on_quit(1))
    ))
    systray.run()


def main():
    # Makes the systray Icon a seperate thread so it doesn't block code
    twrv = Thread(target = sysIcon).start()
    
    ## setup
    global ser
    ser = setupV2()
    
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
            log.critical("Arduino is not plugged in")
            #log.critical("Program quiting, goodbye")
            sys.exit(1) 

        except Exception as e:
            log.warning(e)
            print()
            time.sleep(0.2)

            if type(e) is serial.SerialException:
                log.warning("Arduino disconected, trying to reconect")
                toaster.show_toast("Arduino has been disconected", "Rrying to reconnect", icon_path=None, duration=3, threaded=True)
                print()
                ser = None
                setupV2(3)
                
if __name__ == "__main__":
    DEBUG = 0  # 0 for off 1 for DEBUG logs on
    logger_setup(DEBUG)
    from funcs import log

    main()
