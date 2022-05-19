import serial
import serial.tools.list_ports
import time
import os
import pyautogui
from my_messages import message

import contextlib
import psutil
from pywinauto import Application
import logging
from threading import Thread
import warnings

import Utils
import win32gui, win32process

from ctypes import windll

user32 = windll.user32
user32.SetProcessDPIAware() # optional, makes functions return real pixel numbers instead of scaled values
full_screen_rect = (0, 0, user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))

class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        #print(type(self._target))
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
        name = win32gui.GetWindowText(hWnd)
        if 'YouTube' in name:
            return False
        return rect == full_screen_rect
    except Exception:
        return False

def Change_desktop(direction):
    twrv = ThreadWithReturnValue(target=is_fullscreen, args=())
    twrv.start()
    full = twrv.join()
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
        #pass
 
def Play_pause_V4():    # get PID of focused app
    current_focused_pid, current_focused_pid = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())   
    listOfProcessIds = Utils.findProcessIdByName('Spotify')

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


def main():   # sourcery skip: switch
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
        message("critical", "Cannot connect, quitting program")
        quit()


    while True:
        #try:
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
                pass
            elif button == "2":
                logging.info("Play Pause")
                t = Thread(target=Play_pause_V4, args=()).start()
            elif button == "3":
                logging.info("Move to Left desktop")
                Change_desktop('left')
            elif button == "4":
                logging.info("Move to Right desktop")
                Change_desktop('right')
            # elif button == "5":
            #     pass
            # elif button == "6": 
            #     pass
            # elif button == "7":
            #     pass
            # elif button == "8":
            #     pass
            # elif button == "9":
            #     pass
            # elif button == "0":
            #     pass
            # elif button == "A":
            #     pass

        # except Exception as e:
        #     message("warning", f"Exception raised \n{e}")
        #     print("")
     

if __name__ == "__main__":
    main()