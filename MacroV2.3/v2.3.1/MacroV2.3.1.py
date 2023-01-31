from funcs import *
import pystray
from PIL import Image
import serial.tools.list_ports
import sys
import custom_keyboard
from win10toast import ToastNotifier

"""
TODO
in V2.3.2:
try and transition all pyautogui keyboard funtions to custom_keyboard
add a write function to custom_keyboard
"""

image = Image.open("C:\Coding\Arduino Stuff\Projects\macro_keyboard\MacroV2.3\\v2.3.1\\pythonIcon.ico") 
#https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread-in-python

toaster = ToastNotifier()
NOTIFICATION = {
    "ShowNotification": True,
    "Duration": 1.5
    }

def Button_handler(button):

    def sheild_focus_star_citizen(key): #macro to focus ship shields in star citizen
        log.debug(f"right shift + {key}")
        custom_keyboard.hotkey('shiftright', key)
        time.sleep(0.1)
        custom_keyboard.press('shiftright')

    def change_desktop(direction, focused_app): #change desktop hotkey, where direction is either 'left' or 'right'. Will alt+tab if specific program is focused
        log.debug(f"move desktop {direction}")
        
        apps_to_alt_tab = ('Star Citizen')  #lis of apps to alt tab when changing desktops

        if focused_app in apps_to_alt_tab: 
            custom_keyboard.hotkey('alt', 'tab')
            time.sleep(0.1)
        custom_keyboard.hotkey('ctrl', 'win', direction)

    focused_win_name = win32gui.GetWindowText(user32.GetForegroundWindow())

    win_name = focused_win_name.split(" - ")
    win_name.reverse()

    app = win_name[0]
    if app == '': #Sets app to 'Desktop' if nothing is focused.
        app = 'Desktop'

    # Match case for buttons.
    match [app, button.split()]:
        #Format: 
        #case [AppName, ("ButtonNumber", "MacroMode")]:
        # Leave AppName _ for any app
        # MacroMode as mode for any mode
    
        # Any app and Any Mode    And that are prioritives 
        case [_, ("1", mode)]:    # Shows what each button is defined as
            log.debug("ButtonMode")
            twrv = Thread(target = ButtonMode, args=(mode, )).start()

        case [_, ("2", mode)]:    # pause song spotify for any app
            log.debug("pause song spotify \n")
            spotifyV2()

        case [_, ("3", mode)]:    # move desktop left for any app
            twrv = Thread(target = change_desktop, args=('left', app)).start()

        case [_, ("4", mode)]:     # move desktop right for any app   
            twrv = Thread(target = change_desktop, args=('right', app)).start()


        # Specific app but any Mode
        # VS Code Layer
        case ["Visual Studio Code", ("5", mode)]: # run code in Vs code
            pyautogui.hotkey('ctrl', 'alt', 'n') 

        # Star Citizen Layer
        case ["Star Citizen", ("5", mode)]: # focus front shields
            sheild_focus_star_citizen("1")

        case ["Star Citizen", ("6", mode)]: # focus back shields
            sheild_focus_star_citizen("2")

        case ["Star Citizen", ("7", mode)]: # Reset shields
            sheild_focus_star_citizen("3")


        # Any App, Specific Mode
        case [_, ("5", "2")]:     # Cut (Ctrl + x)
            log.debug("Audacity Cut (Ctrl + x)")
            custom_keyboard.hotkey('ctrl', 'x')
       
        case [_, ("6", "2")]:     # Audacity Split Ctrl + i 
            log.debug("Audacity Split (ctrl + i)")
            custom_keyboard.hotkey('ctrl', 'i')

        case [_, ("9", "2")]:     # Backspace
            log.debug("Backspace")
            custom_keyboard.press('backspace')

        # Macros that are last priority.     
        case [_, ("5", mode)]:   # Text to speech
            log.debug("Text to speech")
            before = pyperclip.paste()
            custom_keyboard.hotkey('ctrl', 'c')
            time.sleep(0.01)
            twrv = Thread(target = textToSpeech, args=([before])).start()
        
        case [_, ("7", mode)]:   # Copy
            log.debug("Copy")
            #NOTE : this can cause a keyboard interupt if used in terminal
            custom_keyboard.hotkey('ctrl', 'c')

        case [_, ("8", mode)]:   # Paste 
            log.debug("Paste")
            custom_keyboard.hotkey('ctrl', 'v')

        case [_, ("0", mode)]:     # runs Task Manager      is button 10
            log.debug("Starting Task manager")
            custom_keyboard.hotkey('ctrl', 'shift', 'esc')
                
        case [_, ("A", mode)]:   #image to text             is button 11
            log.debug("Image to text")
            twrv = Thread(target = Image_to_text).start()

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
            
            if NOTIFICATION["ShowNotification"]:
                toaster.show_toast("Access is denied","Arduino is already connected to something", icon_path=None, duration=NOTIFICATION["Duration"], threaded=True)

            on_quit(0)

        except Exception as e:
        
            log.error(e)
            time.sleep(0.2)
        else:
            log.info("Connected to Arduino")

            if NOTIFICATION["ShowNotification"]:
                toaster.show_toast("Macro Keypad is connected", icon_path=None, duration=NOTIFICATION["Duration"], threaded=True)

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
