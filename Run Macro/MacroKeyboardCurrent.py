from infi.systray import SysTrayIcon
#import serial
import serial.tools.list_ports
from PIL import ImageGrab, Image
import pyperclip
from threading import Thread
import warnings, logging, time
import my_messages as msg
import Utils
import os, win32gui, win32process

from pywinauto import Application, keyboard
## Replace pyautogui with pywinauto   https://pywinauto.readthedocs.io/en/latest/index.html#what-is-it
import pyautogui
from ctypes import windll


import timeit


# C:\Python310\python.exe "C:\Coding\Arduino Stuff\Projects\Arduino Python\Run Macro\MacroKeyboardCurrent.py"

icon_path = "C:\Coding\Python\pythonScript.ico"
Stop = False

user32 = windll.user32
user32.SetProcessDPIAware() # optional, makes functions return real pixel numbers instead of scaled values
full_screen_rect = (0, 0, user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))


class ThreadWithReturnValue(Thread):
    #https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread-in-python
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return


def is_fullscreen():
    try:
        hWnd = user32.GetForegroundWindow()
        rect = win32gui.GetWindowRect(hWnd)
        if 'Google Chrome' in win32gui.GetWindowText(hWnd): # if youtube or google chrome is in the name of the window.
            return False
        return rect == full_screen_rect
    except Exception:
        return False

def Change_desktop(direction): #change desktop hotkey, where direction is either 'left' or 'right'. Will alt+tab is program is in fullscreen mode
    # twrv = ThreadWithReturnValue(target=is_fullscreen, args=())
    # twrv.start()
    # full = twrv.join()
    full = is_fullscreen()
    if full == True:
        pyautogui.hotkey('alt', 'tab')  
    pyautogui.hotkey('ctrl', 'win', direction)      


spotify_PID = None
def focus_v4(ids):
    warnings.filterwarnings("ignore", category=UserWarning)
    try:
        app = Application().connect(process=ids)
        app.window().send_keystrokes(" ")
        global spotify_PID
        spotify_PID = ids

    except Exception as e:
        print(f"Exception Raised: {e}")
 
def Play_pause_V4():    # get PID of focused app
    current_focused_pid = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())   
    listOfProcessIds = Utils.findProcessIdByName('Spotify')

    if spotify_PID in listOfProcessIds:
        print("spotify in")
        focus_v4(spotify_PID)
        return
    if listOfProcessIds != [] and current_focused_pid not in listOfProcessIds:
        # if spotify is running, and spotify not in listOfProcessIds
        # focus spotify
        threads = [None] * len(listOfProcessIds)
        for n in range(len(listOfProcessIds)):
            threads[n] = Thread(target=focus_v4, args=(listOfProcessIds[n],)).start()
        return
    pyautogui.press("playpause")  


def Image_to_text():
    img = ImageGrab.grabclipboard()
    img.save("C:/Users/Taylor/itt/image.png")
    os.system('cmd /c "cd C:\\Users\\Taylor\\itt & tesseract Image.png tesseract-result"')
    
    file = open("C:\\Users\\Taylor\\itt\\tesseract-result.txt", 'r', encoding='utf-8').read()
    # removes the arrow from the text
    if '\n\x0c' in file:
        file = file.replace('\n\x0c','')
    pyperclip.copy(file)


def test():
    t = Thread(target=Play_pause_V4, args=())
    t.start()


### Important

def Connect():
    """
    Tries to connect to the arduino.
    Outputs None if it cant connect.
    """
    logging.info("Connecting to Arduino...")
    
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        if "Arduino Micro" in desc:
            logging.info("Found Arduino Port")
            return port
        logging.info("Arduino is not connected or cannot find arduino.")
        return None

###  NOT SO IMPORTANT

def on_quit(systray):
    """
    Quits the program
    """
    #print("Bye")
    msg.message("critical", "PROGRAM is shutting down")
    global Stop
    Stop = True
    systray.shutdown()
    exit()


def do_example(systray):
    print("Example")

def on_status(systray):
    """
    Gets the connection status
    """
    arduinoPort = Connect()
    Status = "Connected" if arduinoPort != None else "Not connected"
    pyautogui.alert(Status, "Status")  # always returns "OK"

def input_special_char():
    promptText= """ What greek letter, operator or maths operation do you want
    Greek letters   Codes
    Theta                 Theta
    lambda              lambda
    pi                          pi
    Delta                  Delta
    Ohm                   Omega

    Operators       Codes
    Multiply            times
    Divide              div
    Multiply Dot    cdot
    Infinity               infty

    Maths operation Codes:
    Fraction                 frac
    Sqrt                         sqrt
    Root                       rootof
    """ 
    operator = pyautogui.prompt(text=promptText)
    pyautogui.write(f"\{operator}")
    pyautogui.press("space")

def ButtonMode(mode):
    ButtonDescriptions = f"""Current mode is: {mode}
    If button is not their nothing is assigned to it.
    Button 1 is used to show this.

    Mode 1:     General
        Button 2:   Pause/play song spotify
        Button 3:   Switches desktop to the left
        Button 4:   Switches desktop to the right
        Button 5:   Next Song Spotify
        Button 6:   Previous song Spotify
        Button 7:   Volume Up
        Button 8:   Volume Down
        Button 9:   Copy
        Button 10:  Paste
        Button 11:  Converts screenshot of text to text

    Mode 2:     Math on google Docs
        Button 3:   Switches desktop to the left
        Button 4:   Switches desktop to the right
        Button 7:   Insert new equation in google docs
        Button 8:   Inserts special Char in equation
                    Ex; multiply or fraction
        Button 9:   Copy
        Button 10:  Paste
        Button 11:  Converts screenshot of text to text

    Mode 3 and 4 do nothing 
    """
    pyautogui.alert(ButtonDescriptions, "Button Mode")  


### Super Important
def main():   # sourcery skip: switch
    menu_options = (("Example", None, do_example),
                    ("Status", None, on_status))
    systray = SysTrayIcon(icon_path, "Python Macro", menu_options ,on_quit)
    systray.start()

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    arduinoPort = Connect()

    # Checks if arduino is already connected.
    try: 
        ser = serial.Serial(arduinoPort, 9600)
        logging.info("Connected to Arduino\n")
    except (serial.SerialException):
        logging.info("The arduino is already connected.")
        msg.message("critical", "Cannot connect, quitting program")
        exit()


    while Stop == False:
        try:
            cc=str(ser.readline())
            fullButtton = cc[9:-5]
            button = fullButtton[-3]
            mode = fullButtton[-1]

            """
            There are buttons 1 thru 12
            10 is 0
            11 is A
            12 is B
            """

            if button == '1':
                ButtonMode(f"Mode {mode}")
            if button == "3":
                Change_desktop('left')
                #print(timeit.timeit('Change_desktop("left")',setup='from __main__ import Change_desktop', number=1))
            elif button == "4":
                Change_desktop('right')
                #print(timeit.timeit('Change_desktop("right")',setup='from __main__ import Change_desktop', number=1))
            elif button == "9":    # Copy
                pyautogui.hotkey('ctrl', 'c') 
            elif button == "0":   # Paste 
                pyautogui.hotkey('ctrl', 'v')  
            elif button == "A": #image to text
                Image_to_text()

            if mode == "1":
                if button == "2": # pause song spotify
                    global t
                    t = Thread(target=Play_pause_V4, args=())
                    t.start()
                    #print(timeit.timeit(stmt='t.start()', setup='', number=1, globals=globals()))
                elif button == "5":    # Next song Spotify
                    pyautogui.press("nexttrack")
                    #print(timeit.timeit(stmt='pyautogui.press("nexttrack")', number=1, globals=globals()))
                elif button == "6":   # previous song Spotify 
                    pyautogui.press("prevtrack")
                    #print(timeit.timeit(stmt='pyautogui.press("prevtrack")', number=1, globals=globals()))
                elif button == "7":    # Volume Up 
                    pyautogui.hotkey('volumeup')    
                    #print(timeit.timeit(stmt='pyautogui.press("volumeup")', number=1, globals=globals()))
                elif button == "8":    # Volume Down
                    pyautogui.hotkey('volumedown')  
                    #print(timeit.timeit(stmt='pyautogui.press("volumedown")', number=1, globals=globals()))


            # math
            if mode == "2":
                if button == "7":     # insert new equation in google docs
                    pyautogui.hotkey('alt', 'i') 
                    time.sleep(0.1)
                    pyautogui.press('e') 
                elif button == "8":
                    input_special_char()



        except Exception as e:
            msg.message("warning", f"Exception raised \n{e}")
            print("")

            if type(e) == serial.SerialException:
                msg.message("warning", "Arduino has been disconected, attempting to reconnect")
                arduinoPort = Connect()
                while True:
                    try:
                        ser = serial.Serial(arduinoPort, 9600)
                    except Exception:
                        logging.info("Could not connect trying again")
                        time.sleep(2)
                    else:
                        logging.info("Connected to Arduino\n")
                        break
            

if __name__ == "__main__":
    main()