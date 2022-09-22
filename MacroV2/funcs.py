import contextlib
import threading
from threading import Thread
import warnings
import psutil
import pyautogui
import os, win32gui, win32process
import pyperclip
from pywinauto import Application
from ctypes import windll
from PIL import ImageGrab
import logging
import time
#from tqdm import tqdm

user32 = windll.user32
user32.SetProcessDPIAware() # optional, makes functions return real pixel numbers instead of scaled values
full_screen_rect = (0, 0, user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))

#Custom logger
class CustomFormatter(logging.Formatter):
    MAGENTA = "\u001b[35m"
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = '%(asctime)s.%(msecs)03d %(levelname)s - %(funcName)s: %(message)s'

    FORMATS = {
        logging.DEBUG: MAGENTA + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt='%H:%M:%S')
        return formatter.format(record)

def logger_setup(level):
    # create logger with 'spam_application'
    global log
    log = logging.getLogger("My_app")

    if level == 0:
        log.setLevel(logging.INFO)
    else:
        log.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    if level == 0:
        ch.setLevel(logging.INFO)
    else:
        ch.setLevel(logging.DEBUG)
        
    ch.setFormatter(CustomFormatter())
    log.addHandler(ch)

# log.debug("debug message")
# log.info("info message")
# log.warning("warning message")
# log.error("error message")
# log.critical("critical message")



### find PID of app, 
def findProcessIdByName(processName):
    """
    Returns a list of all the process ID's with a specific name.
    
    Args:
        processName (str) - Name of the process you want to find.
        Ex: "Spotify"
        
    Returns:
        (listOfProcessIds) List of all process ID's with a specific name.

    NOTE: Function will not work if processName is empty
    """
    listOfProcessIds = []
    for proc in psutil.process_iter():
        with contextlib.suppress(psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pinfo = proc.as_dict(attrs=['pid', 'name'])
            if processName.lower() in pinfo['name'].lower() :
                listOfProcessIds.append(pinfo['pid'])
    return listOfProcessIds

def is_fullscreen():
    try:
        hWnd = user32.GetForegroundWindow()
        rect = win32gui.GetWindowRect(hWnd)
        if 'Google Chrome' in win32gui.GetWindowText(hWnd): # if youtube or google chrome is in the name of the window.
            return False
        return rect == full_screen_rect
    except Exception:
        return False



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
    listOfProcessIds = findProcessIdByName('Spotify')

    if spotify_PID in listOfProcessIds:
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



def Change_desktop(direction): #change desktop hotkey, where direction is either 'left' or 'right'. Will alt+tab is program is in fullscreen mode
    # twrv = ThreadWithReturnValue(target=is_fullscreen, args=())
    # twrv.start()
    # full = twrv.join()
    full = is_fullscreen()
    if full == True:
        pyautogui.hotkey('alt', 'tab')  
    pyautogui.hotkey('ctrl', 'win', direction)      


def Image_to_text():
    img = ImageGrab.grabclipboard()
    img.save("C:/Users/Taylor/itt/image.png")
    os.system('cmd /c "cd C:\\Users\\Taylor\\itt & tesseract Image.png tesseract-result"')
    
    file = open("C:\\Users\\Taylor\\itt\\tesseract-result.txt", 'r', encoding='utf-8').read()
    # removes the arrow from the text
    if '\n\x0c' in file:
        file = file.replace('\n\x0c','')
    pyperclip.copy(file)

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
        
    Default:
        Button 1 is used to show this.
        Button 2:   Pause/play, next or previous song spotify 
        Button 3:   Switches desktop to the left
        Button 4:   Switches desktop to the right
        Button 5:   
        Button 6:   
        Button 7:   
        Button 8:   
        Button 9:   Copy
        Button 10:  Paste
        Button 11:  Converts screenshot of text to text

    When in Vscode:
        Button 5:   run code in Vs code

    When in Star Citizen:
        Button 5: focus front shields  
        Button 6: focus back shields
        Button 7: Reset shields
        
    Mode 2, 3 and 4 do nothing   
    """
    pyautogui.alert(ButtonDescriptions, "Button Mode")  


def cpu_ram_monitor():
    """
    Prints a progress bar in terminal showing cpu, ram usage, also the cpu usage of the procces.    
    
    To use properly, thread it as a daemon so it quits when main thread quits.

    Examples
        --------
        >>> from threading import Thread
        >>> from tqdm import tqdm
        >>> import time, psutil, os
        >>>
        >>> monitor = Thread(target=cpu_ram_monitor, daemon=True)
        >>> monitor.start()
    """
    # python_process = psutil.Process(os.getpid())
    # with tqdm(total=100, desc='pros%', position=2) as prosbar, tqdm(total=100, desc='cpu%', position=1) as cpubar, tqdm(total=100, desc='ram%', position=0) as rambar:
    #     while True:
    #         rambar.n=psutil.virtual_memory().percent
    #         cpubar.n=psutil.cpu_percent()
    #         prosbar.n=python_process.cpu_percent()
    #         rambar.refresh()
    #         cpubar.refresh()
    #         prosbar.refresh()
    #         time.sleep(0.25)

count =0
def spotify(timeout = 0.5):
    """Plays/Pauses spotify, presses next song previous song.   
    
    Press 1 time in timeout seconds to Plays/Pauses.     
     Press 2 times in timeout seconds to get next song.  
    Press 3 times in timeout seconds to get previous song.   

    Args:
      timeout (integer): Defines how much time you have
       to press the button for it to do something
    Returns:
      None
    """
    thread_running = None
    global count
    count += 1

    def spotify_timer(timeout):
        time.sleep(timeout)
        global count
        if count == 1:
            log.debug("play pause")
            twrv = Thread(target=Play_pause_V4, args=()).start()
            #twrv.start()
        elif count == 2:
            log.debug("next song")
            pyautogui.press("nexttrack")
        elif count == 3:
            log.debug("previous song")
            pyautogui.press("prevtrack")

        count =0

    sp_tmr = Thread(target=spotify_timer, args=(timeout,),daemon=True)
    # checks if the thread is running
    for thread in threading.enumerate():
        t_name = thread.name
        if threading.active_count() == 1:
            thread_running = False
            continue
        if t_name == 'MainThread':
            continue
        if '(spotify_timer)' in t_name:
            thread_running = True
            break
        elif '(spotify_timer)' not in t_name:
            thread_running = False

    if thread_running is False:
        sp_tmr.start()



