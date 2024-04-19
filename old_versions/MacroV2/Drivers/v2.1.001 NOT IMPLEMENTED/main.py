#from logger import logger
from macro_driver import MacroDriver

import pystray
import os
from PIL import Image
import threading


script_path = os.path.dirname(__file__)

#it is the folder the script is in, will need to change if parent folder is different
version = __file__.split('\\')[-2]

# Gets the path of icon image
icon_path = fr"{script_path}\pythonIcon.ico"
image = Image.open(icon_path)    # Opens the Icon 
#https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread-in-python

def sysIcon():
    systray = pystray.Icon(name="Python Macro", icon=image, title=f"Python Macro{version}", menu=pystray.Menu(
        pystray.MenuItem("Quit", lambda: macro_driver.stop())
    ))
    systray.run()


def main():
    twrv = threading.Thread(target = sysIcon, daemon=True).start()

    global macro_driver
    # Create a new macro driver
    macro_driver = MacroDriver()

    # Start the macro driver
    macro_driver.start()

if __name__ == '__main__':
    main()

    """
    Changelog:
        This should now work with 'should_work.ino'
        I have not tried it yet, am afraid to break the code on the arduino as I don't have the code that is currently on it.

        the mode is now handled by the driver and not the arduino

    

    TODO:
        Work on rocket flying   https://www.youtube.com/watch?v=ItN-K-WSCkM 
        wellskate macro too

        try and transition all pyautogui keyboard funtions to custom_keyboard
        add a write function to custom_keyboard


    """