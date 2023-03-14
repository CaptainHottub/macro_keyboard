import contextlib
import logging

from functools import wraps

import custom_keyboard
import threading
import ctypes
import ctypes.wintypes as wintypes
import time

import os
from PIL import Image, ImageGrab

# Ctypes Stuff
WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

EnumWindows = ctypes.WinDLL('user32').EnumWindows
EnumWindows.argtypes = WNDENUMPROC, wintypes.LPARAM  # LPARAM not INT
EnumWindows.restype = wintypes.BOOL

GetWindowText = ctypes.WinDLL('user32').GetWindowTextW
GetWindowTextLength = ctypes.WinDLL('user32').GetWindowTextLengthW

IsWindow = ctypes.WinDLL('user32').IsWindow

GetWindowThreadProcessId = ctypes.WinDLL('user32').GetWindowThreadProcessId
ctypes.WinDLL('user32').GetWindowThreadProcessId.restype = wintypes.DWORD
ctypes.WinDLL('user32').GetWindowThreadProcessId.argtypes = (
        wintypes.HWND,     # _In_      hWnd
        wintypes.LPDWORD,) # _Out_opt_ lpdwProcessId


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


def filter_process_list(process_to_find: str, process_list):
    """         loops thru the list to find processes with name you want        \n
    Returns list of dictionarys containing processes with process_to_find in name \n
    Returns empty list if there are none
    """
    logger.debug("filter_process_list")
    return [
            proc 
            for proc in process_list
            if process_to_find.lower() in proc['Title'].lower()
            ]


def get_processes(sort = False):
    """Returns list of dictionarys of all apps, their PIDS and hwnd\n
    leave empty if you want the whole list
    Put True in if you want the list sorted by title
    """

    @WNDENUMPROC
    def py_callback( hwnd, lparam ):
        pid = wintypes.DWORD()
        tid = GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if IsWindow(hwnd):
            length = GetWindowTextLength(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            GetWindowText(hwnd, buff, length + 1) 

            if buff.value and buff.value not in ['Default IME', 'MSCTFIME UI']:
                results.append({"Title": buff.value,
                                "PID": tid,
                                "HWND": hwnd})
        return True

    results = []
    EnumWindows(py_callback,0)

    if sort:
        logger.debug("sorting")
        resultslist = sorted(results, key=lambda d: d['Title'])
        return resultslist

    return results


def spotifyV3(timeout = 0.4, count=[0]):
    """Plays/Pauses spotifyV3, presses next song previous song.   
    
    Press 1 time in timeout seconds to Plays/Pauses.        \n
    Press 2 times in timeout seconds to get next song.      \n
    Press 3 times in timeout seconds to get previous song.  \n   

    Args:
      timeout (integer): Defines how much time you have to press the button for it to do something
      count (list): Don't touch this, it is a counter for the function
    Returns:
      None
    """
    count[0] += 1
    
    logger.debug("Spotify Func Has been called")

    def spotify_timerV3():
        """Waits for timeout to finish then it send a keyboard input based on value of count[0]"""

        logger.debug("spotify_timer Has just begun")
        time.sleep(timeout)
        logger.debug("spotify_timer sleep has just finished")

        actions = [
            "playpause",
            "nexttrack",
            "prevtrack"]
        
        logger.debug("Entering try")
        try:
            action = actions[count[0]-1]
        
            custom_keyboard.press(action)  
            logger.debug(f'Value of {count[0] = }, executing folowing action: {action}')

        except IndexError as ind:
            print('\n')
            logger.error(f'IndexError has just happened, reason: {ind}')
            logger.error(f'Button was pressed to many times. You pressed it {count[0]} times.\n')

        except Exception as e:
            logger.error(e)
        
        finally:
            count[0] = 0
            logger.debug(f"Value of {count[0] = }\n")

    """         Finds if thread I want is running, if not it starts, if it is does nothing          """
    # adds True to list if func hmm is running as a thread
    thread_running = [
        True
        for thread in threading.enumerate()
        if spotify_timerV3.__name__ in thread.name
        ]
    
    if not any(thread_running):
        logger.debug("Thread I want is not running, starting it")
        spotify_thread = threading.Thread(target=spotify_timerV3, args=(),daemon=True)
        spotify_thread.start()
    else:
        logger.debug("thread I want is running")

import pytesseract
import pyperclip
from pynput import mouse, keyboard
m = mouse.Controller()

def imt():
    """Presses Win Shif S to open snippet mode, waits for mouse release then does tesseract OCR
    Press Ctrl V to paste text
    """
    logger.debug("imt has just started")

    def on_release(key):
        if key == keyboard.Key.esc:
            logger.debug('esc pressed and released')
            # Stop listener and the program
            m.click(mouse.Button.left,1)
            return False

    keyboard_listener = keyboard.Listener(
        on_release=on_release)
    
    custom_keyboard.hotkey('winleft', 'shift', 's')
    time.sleep(0.2)

    keyboard_listener.start()

    mouse_clicks = []   
                
    with mouse.Events() as events:
        for event in events:
            with contextlib.suppress(Exception):
                if event.button == mouse.Button.left:
                    text = {
                        'x': event.x,
                        'y': event.y,
                        'button': str(event.button),
                        'pressed': event.pressed}
                    mouse_clicks.append(text)
                    if event.pressed == False:
                        break
    
    pressed =  keyboard_listener.is_alive()
    if not pressed:
        print("keyboard_listener is not running")
        return False
    
    #checks if the mouse moved
    click1, click2 = mouse_clicks
    dx = click1['x'] - click2['x']
    dy = click1['y'] - click2['y']
    if dx == 0 and dy == 0:
        print("mouse didnt move")
        return False
    
    time.sleep(0.1)
    
    # grabs the image from clipboard and converts the image to text.
    img = ImageGrab.grabclipboard()
    text = pytesseract.image_to_string(img)
    text = text.replace('\x0c', '')
    pyperclip.copy(text)


if __name__ == '__main__':
    logger.debug("__name__ == '__main__'")

    # TODO    



    # WORKS

    # filtered_list = filter_process_list('chrome', get_processes())
    # print(*filtered_list, sep='\n')

    # # play
    # spotifyV3()
    # time.sleep(1)

    # #pause
    # spotifyV3()
    # time.sleep(1)
    
    # imt()