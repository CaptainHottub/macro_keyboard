import concurrent.futures
import math
import os
from socket import MsgFlag, timeout
from pywinauto import Application
import logging
from threading import Thread
import concurrent.futures
import warnings
import pyautogui
import time

import Utils

from my_messages import message


from ctypes import windll
import win32gui, win32process
from pywinauto import Application

#https://stackoverflow.com/questions/26241540/python-check-if-application-is-in-fullscreen

user32 = windll.user32
user32.SetProcessDPIAware() # optional, makes functions return real pixel numbers instead of scaled values
full_screen_rect = (0, 0, user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))


def is_full_screen():
    try:
        hWnd = user32.GetForegroundWindow()
        rect = win32gui.GetWindowRect(hWnd)
        return rect == full_screen_rect
    except:
        return False

class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        print(type(self._target))
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return

def Change_desktop(direction):
    time.sleep(3)
    twrv = ThreadWithReturnValue(target=is_full_screen, args=()).start()
    #twrv.start()
    full = twrv.join()
    if full == True:
        pyautogui.hotkey('alt', 'tab')  
    pyautogui.hotkey('ctrl', 'win', direction)  



if __name__ == '__main__':
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    Change_desktop('right')


