

# import contextlib
# import psutil
from pywinauto import Application
import logging
import threading
import warnings

import Utils
import win32gui, win32process

## Replace pyautogui with pywinauto   https://pywinauto.readthedocs.io/en/latest/index.html#what-is-it
import pyautogui


spotify_PID = None

def focus_v3(ids):
    pos = pyautogui.position()
    warnings.filterwarnings("ignore", category=UserWarning)
    #message("debug", f"focus_v3 has begun for {ids}")
    try:
        app = Application().connect(process=ids)
        app.top_window().set_focus()
        pyautogui.moveTo(pos)

    except Exception as e:
        #print(f"Thread {ids}: FAILED\n")
        #logging.info(f"Exception is: {e}")

        #return False
        pass

    else:
        #print(f"Thread {ids}: finished\n")
        global spotify_PID
        spotify_PID = ids
        pyautogui.press("playpause")


def Play_pause_V3():
    # press's play/pause, it will focus spotify if it is running.
    logging.info("Play_pause started")
    global spotify_PID
    listOfProcessIds = Utils.findProcessIdByName('Spotify')

    if listOfProcessIds != []:
        if spotify_PID is None or spotify_PID not in listOfProcessIds:
            # if PID is Not valid, need to find valid one
            threads = [None] * len(listOfProcessIds)
            for n in range(len(listOfProcessIds)):
                threads[n] = threading.Thread(target=focus_v3, args=(listOfProcessIds[n],)).start()

            logging.info("Finished")
            return 

        # can use standard thready for focus
        x = threading.Thread(target=Utils.focus_v3, args=(spotify_PID,))
        x.start()
        logging.info("Finished")
        return
    
    #message("debug", "Spotify is NOT running")
    pyautogui.press("playpause")

