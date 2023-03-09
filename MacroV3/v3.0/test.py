import logging
import datetime
from functools import wraps

import custom_keyboard
import threading
import psutil
import pyautogui
import win32gui
import win32process
from ctypes import *
import ctypes.wintypes as wintypes
import time
from pywinauto import Application


# user32 = ctypes.windll.user32
# user32.SetProcessDPIAware() # optional, makes functions return real pixel numbers instead of scaled values
# full_screen_rect = (0, 0, user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))



# Ctypes Stuff
WNDENUMPROC = WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

EnumWindows = WinDLL('user32').EnumWindows
EnumWindows.argtypes = WNDENUMPROC, wintypes.LPARAM  # LPARAM not INT
EnumWindows.restype = wintypes.BOOL

GetWindowText = WinDLL('user32').GetWindowTextW
GetWindowTextLength = WinDLL('user32').GetWindowTextLengthW
IsWindowVisible = WinDLL('user32').IsWindowVisible
IsWindow = WinDLL('user32').IsWindow
WinDLL('user32').GetWindowThreadProcessId.restype = wintypes.DWORD
WinDLL('user32').GetWindowThreadProcessId.argtypes = (
        wintypes.HWND,     # _In_      hWnd
        wintypes.LPDWORD,) # _Out_opt_ lpdwProcessId

GetForegroundWindow = WinDLL('user32').GetForegroundWindow

# for manipulating the desktop. Needs VirtualDesktopAccessor.dll to work
# https://github.com/Ciantic/VirtualDesktopAccessor#:~:text=Reference%20of%20exported%20DLL%20functions
vda = windll.LoadLibrary("C:\\Coding\\Python\\StartSchool\\VirtualDesktopAccessor.dll")
IsWindowOnCurrentVirtualDesktop = vda.IsWindowOnCurrentVirtualDesktop       #pass hwnd as arg and will return 1 or 0
GetCurrentDesktopNumber = vda.GetCurrentDesktopNumber   #No args needed, returns int,
MoveWindowToDesktopNumber = vda.MoveWindowToDesktopNumber
GoToDesktopNumber = vda.GoToDesktopNumber       # moves you to desktop specified by arg





#Custom logger format, 
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

# create logger
logger = logging.getLogger("My_app")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s - %(funcName)s: %(message)s', datefmt='%H:%M:%S') 
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(CustomFormatter())
logger.addHandler(stream_handler)


def get_time(func):
    """Times any function\n
    Use as decorator to time funcs\n
    @get_time """
    
    @wraps(func)
    def timer(*args, **kwargs):
        start_time = time.perf_counter()

        results = func(*args, **kwargs)
    
        end_time = time.perf_counter()
        total_time = round(end_time - start_time, 6)

        func_name = func.__name__
        logger.info(f'{func_name} took {total_time} seconds to complete')

        return results
    
    return timer 

from statistics import mean
def multi_time(func, x: int):
    """Times func x number of times and returns the mean"""

    logger.info(f'Starting timing for {func.__name__} {x} times')
    
    def timer(*args, **kwargs):
        start_time = time.perf_counter()

        results = func(*args, **kwargs)

        end_time = time.perf_counter()

        total_time = round(end_time - start_time, 6)    

        times.append(total_time)
        
    times = []
    for i in range(x):
        timer()
    logger.info(f'Timing for {func.__name__} has finished')
    return mean(times)





### find PID of app, 
def findProcessIdByName(processName): # This returns the parent of the procces Name, 
    """
    Returns a list of all the process ID's with a specific name.
    
    Args:
        processName (str) - Name of the process you want to find.
        Ex: "Spotify"
        
    Returns:
        (listOfProcessIds) List of all process ID's with a specific name.

    NOTE: Function will not work if processName is empty

    try:
    for p in psutil.process_iter(['name']):
        if processName in p.info['name']:
            parent = p.parent()
            if parent != None:
                return parent.pid
            
    except Exception as e:
        logger.error(f"Exception Raised: {e}")
        return None
    """
    listOfProcessIds = []
    for proc in psutil.process_iter():
        pinfo = proc.as_dict(attrs=['pid', 'name'])
        if processName.lower() in pinfo['name'].lower() :
            listOfProcessIds.append(pinfo['pid'])
    return listOfProcessIds



count =0
spotify_PID = None
def spotifyV2(timeout = 0.4):
    """Plays/Pauses spotifyV2, presses next song previous song.   
    
    Press 1 time in timeout seconds to Plays/Pauses.     
     Press 2 times in timeout seconds to get next song.  
    Press 3 times in timeout seconds to get previous song.   
     If Spotify is not running presses 2 and 3 will be ignored and play/pause will happen

    Args:
      timeout (integer): Defines how much time you have
       to press the button for it to do something
    Returns:
      None
    """
    logger.debug("Spotify Func Has been called")

    thread_running = None
    global count
    count += 1

    def get_spotify_stats():
        logger.debug("get_spotify_stats Has just started")
        
        try:
            logger.debug("Getting Current focused PID")
            global current_focused_pid
            current_focused_pid = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())
            logger.debug(f"Current Focused PID is: {current_focused_pid}")

            logger.debug("Check If Spotify is running")
            for p in psutil.process_iter(['name']):
                if 'Spotify' in p.info['name'] and p.parent() != None:
                    logger.debug("Spotify is running")

                    global spotify_PID
                    spotify_PID = p.parent().pid

                    logger.debug(f"Spotify PID is: {spotify_PID}")
                    break
            else:
                logger.debug("Spotify is not running")
                spotify_PID = None
                return
            
        except Exception as e:
            logger.error(f"Exception Raised: {e}")


    def spotify_timerV2(timeout):
        logger.debug("spotify_timer Has just begun")
        time.sleep(timeout)
        logger.debug("spotify_timer sleep has just finished")

        global count

        # True is spotify is focused, and False if not
        spotify_focussed = spotify_PID in current_focused_pid

        if spotify_PID is None: #Spotify is not running
            logger.debug("Spotify is not running")
            pyautogui.press("playpause")  
            return
        
        app = Application().connect(process=spotify_PID)
        match [count, spotify_focussed]: #spotify is Running, 
            case [1, True]: #count is 1, and focused
                logger.debug("spotify is Running, count is 1, and focused")
                custom_keyboard.press("playpause")  

            case [1, False]: #count is 1, and not focused
                logger.debug("spotify is Running, count is 1, and not focused")
                #pyautogui.press("playpause")  
                app.window().send_keystrokes(" ")
       

            case [2, _]: #count is 2, and any focused
                logger.debug("spotify is Running, count is 2, and any focused")
                logger.debug("next song")
                #pyautogui.press("nexttrack")  
                #app.window().send_keystrokes("c")
                custom_keyboard.press("nexttrack")  

                
            case [3, _]: #count is 3, and any focused
                logger.debug("spotify is Running, count is 3, and any focused")
                logger.debug("previous song")
                #pyautogui.press("prevtrack")  
                #app.window().send_keystrokes("c")
                custom_keyboard.press("prevtrack")  


        
        logger.debug(f"Value of {count = }")
        count =0
        logger.debug(f"Value of {count = } ")
        print("\n")

    
    sp_tmrV2 = threading.Thread(target=spotify_timerV2, args=(timeout,),daemon=True)
    sp_stat = threading.Thread(target=get_spotify_stats, args=(),daemon=True)
    logger.debug("sp_tmrV2 and sp_stat has been defined")

    logger.debug("Check if thread is running")
    for thread in threading.enumerate():
        if '(spotify_timerV2)' in thread.name or '(get_spotify_stats)' in thread.name:
            logger.debug("Spotify timer and or spotify stats thread are running")
            thread_running = True
            break
        else:
            logger.debug("Thread I want is not running")
            thread_running = False

    logger.debug("Just passed Check if thread is running")
    logger.debug(f"thread_running value is: {thread_running}")

    if thread_running is False:
        logger.debug("thread_running is False")
        logger.debug("Starting: sp_tmr.start(), and sp_stat.start()")
        sp_tmrV2.start()
        sp_stat.start()


# @get_time
# def find_app_1():
#     """Looks for Spotify in process list\n
#     spotify_PID will be none if spotify is not running\n
#     spotify_PID will be the PID of the parent app if it is running.
#     """
#     #logger.debug("Check If Spotify is running")
#     for p in psutil.process_iter(['name']):
#         if 'Spotify' in p.info['name'] and p.parent() != None:
#             #logger.debug("Spotify is running")

#             global spotify_PID
#             spotify_PID = p.parent().pid

#             #logger.debug(f"Spotify PID is: {spotify_PID}")
#             break
#     else:
#         #logger.debug("Spotify is not running")
#         spotify_PID = None
#         return

# @get_time
# def find_app_2():
#     """Returns list of all apps and their PIDS"""
#     listOfProcess = []
#     for proc in psutil.process_iter():
#         pinfo = proc.as_dict(attrs=['pid', 'name'])
#         listOfProcess.append(pinfo)
#         #print(proc)
#         #listOfProcessIds.append(pinfo['pid'])
#     return listOfProcess


def get_processes(sorted = False): # you win
    """Returns list of all apps, their PIDS and hwnd"""
    print(sorted)

    @WNDENUMPROC
    def py_callback( hwnd, lparam ):
        pid = wintypes.DWORD()
        tid = windll.user32.GetWindowThreadProcessId(hwnd, byref(pid))
        if IsWindow(hwnd):
            length = GetWindowTextLength(hwnd)
            buff = create_unicode_buffer(length + 1)
            GetWindowText(hwnd, buff, length + 1)
            if buff.value:
                results.append({"Title": buff.value,
                                "PID": tid,
                                "HWND": hwnd})
        return True
    results = []
    EnumWindows(py_callback,0)

    if sorted:
        print("sorting")
        resultslist = sorted(results, key=lambda d: d['Title'])
        return resultslist

    return results

count =0
spotify_PID = None
def spotifyV3(timeout = 0.4):
    """Plays/Pauses spotifyV2, presses next song previous song.   
    
    Press 1 time in timeout seconds to Plays/Pauses.     
     Press 2 times in timeout seconds to get next song.  
    Press 3 times in timeout seconds to get previous song.   
     If Spotify is not running presses 2 and 3 will be ignored and play/pause will happen

    Args:
      timeout (integer): Defines how much time you have
       to press the button for it to do something
    Returns:
      None
    """
    logger.debug("Spotify Func Has been called")

    thread_running = None
    global count
    count += 1

    def get_spotify_stats():
        logger.debug("get_spotify_stats Has just started")
        
        try:
            logger.debug("Getting Current focused PID")
            global current_focused_pid
            current_focused_pid = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())
            logger.debug(f"Current Focused PID is: {current_focused_pid}")

            logger.debug("Check If Spotify is running")
            for p in psutil.process_iter(['name']):
                if 'Spotify' in p.info['name'] and p.parent() != None:
                    logger.debug("Spotify is running")

                    global spotify_PID
                    spotify_PID = p.parent().pid

                    logger.debug(f"Spotify PID is: {spotify_PID}")
                    break
            else:
                logger.debug("Spotify is not running")
                spotify_PID = None
                return
            
        except Exception as e:
            logger.error(f"Exception Raised: {e}")


    def spotify_timerV2(timeout):
        logger.debug("spotify_timer Has just begun")
        time.sleep(timeout)
        logger.debug("spotify_timer sleep has just finished")

        global count

        # True is spotify is focused, and False if not
        spotify_focussed = spotify_PID in current_focused_pid

        if spotify_PID is None: #Spotify is not running
            logger.debug("Spotify is not running")
            pyautogui.press("playpause")  
            return
        
        app = Application().connect(process=spotify_PID)
        match [count, spotify_focussed]: #spotify is Running, 
            case [1, True]: #count is 1, and focused
                logger.debug("spotify is Running, count is 1, and focused")
                custom_keyboard.press("playpause")  

            case [1, False]: #count is 1, and not focused
                logger.debug("spotify is Running, count is 1, and not focused")
                #pyautogui.press("playpause")  
                app.window().send_keystrokes(" ")
       

            case [2, _]: #count is 2, and any focused
                logger.debug("spotify is Running, count is 2, and any focused")
                logger.debug("next song")
                #pyautogui.press("nexttrack")  
                #app.window().send_keystrokes("c")
                custom_keyboard.press("nexttrack")  

                
            case [3, _]: #count is 3, and any focused
                logger.debug("spotify is Running, count is 3, and any focused")
                logger.debug("previous song")
                #pyautogui.press("prevtrack")  
                #app.window().send_keystrokes("c")
                custom_keyboard.press("prevtrack")  


        
        logger.debug(f"Value of {count = }")
        count =0
        logger.debug(f"Value of {count = } ")
        print("\n")

    
    sp_tmrV2 = threading.Thread(target=spotify_timerV2, args=(timeout,),daemon=True)
    sp_stat = threading.Thread(target=get_spotify_stats, args=(),daemon=True)
    logger.debug("sp_tmrV2 and sp_stat has been defined")

    logger.debug("Check if thread is running")
    for thread in threading.enumerate():
        if '(spotify_timerV2)' in thread.name or '(get_spotify_stats)' in thread.name:
            logger.debug("Spotify timer and or spotify stats thread are running")
            thread_running = True
            break
        else:
            logger.debug("Thread I want is not running")
            thread_running = False

    logger.debug("Just passed Check if thread is running")
    logger.debug(f"thread_running value is: {thread_running}")

    if thread_running is False:
        logger.debug("thread_running is False")
        logger.debug("Starting: sp_tmr.start(), and sp_stat.start()")
        sp_tmrV2.start()
        sp_stat.start()


if __name__ == '__main__':
    logger.debug("__name__ == '__main__'")
    
    processes_list = get_processes()
    newlist = sorted(processes_list, key=lambda d: d['Title'])
    #print(get_processes().sort(key= ['Title']))

    #print(*newlist, sep='\n')

    processes_list = get_processes(True)
    #print(*processes_list, sep='\n')


    
