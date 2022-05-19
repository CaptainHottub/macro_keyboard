from ctypes import windll
from threading import Thread
import threading
import funcs
import time
import pyautogui, sys
import os, win32gui, win32process

import serial.tools.list_ports
from ctypes import windll

funcs.logger_setup(1)
from funcs import log

user32 = windll.user32
user32.SetProcessDPIAware() # optional, makes functions return real pixel numbers instead of scaled values
full_screen_rect = (0, 0, user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))

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
    # matches the focused app   #layers
    match [app, button.split()]:
        case [_, [btn, mode]]:
            match button.split():
                #case ["1", ("1" | "2" | "3" | "4") as mode]:
                # basically if button[0] is 1 and if button[1] is 1 thru 4, also defined mode as button[1]
                
                # once its pressed, count how many times you pressed it in limited time
                # grab time in nanoseconds or milliseconds when button is first pressed
                # then when its pressed again check if it was pressed in a specific amount of time. lets say 500 milliseconds (0.5 seconds)
                # 
                # if start_time == None:
                #    start_time = time.perf_counter_ns()
                # 
                # in_between = current_time - start_time
                # if in_between < 500(milliseconds):
                #   count+=1 
                # if in_between > 500(milliseconds): TIME HAS PASSED
                #   start_time = None
                #   IF COUNT ==1 : play pause
                #   IF COUNT ==2 : next song
                #   IF COUNT ==3 : previous song
                #

                case ["2", "1"]: # pause song spotify
                    log.debug("pause song spotify")
                    funcs.spotify()
                    #twrv = Thread(target=funcs.Play_pause_V4, args=())
                    #twrv.start()

                case ["3", ("1" | "2" | "3" | "4") as mode]:    # move desktop left
                    log.debug("move desktop left")
                    twrv = Thread(target=funcs.Change_desktop, args=('left',))
                    twrv.start()

                case ["4", ("1" | "2" | "3" | "4") as mode]:     # move desktop right   
                    log.debug("move desktop Right")
                    twrv = Thread(target=funcs.Change_desktop, args=('right',))
                    twrv.start()
                
                case _:
                    print("there is no macro for that button")


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

def main():
    ser = Connect()
    while True:
        try: 
            cc = str(ser.readline())
            if 'mode button was pressed' in cc:
                log.info(cc)
                continue

            global button
            button = (f"{cc[9]} {cc[11]}")

            Button_handler(button)

        except [serial.serialutil.PortNotOpenError, KeyboardInterrupt]:
            log.critical("Program quiting, goodbye")
            sys.exit(1) 

        except Exception as e:
            log.warning(e)
            print()

            if type(e) is serial.SerialException:
                log.warning("Arduino disconected")
                sys.exit(1) 
       
    
    

if __name__ == "__main__":
    main()