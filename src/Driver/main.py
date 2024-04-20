#from logger import logger
from macro_driver import MacroDriver

import pystray
import os
from PIL import Image
import threading


def get_version():
    try:
        string_with_version_in_it = ''
        with open('CHANGELOG.md','r') as file:
            for line in file:
                if '##' in line:
                    string_with_version_in_it = line
                    file.close()
                    break    
                
        version = string_with_version_in_it[4:12]
    except FileNotFoundError:
        print('CHANGELOG.md Not Found, version will be ""')
        version = ''

    return version

script_path = os.path.dirname(__file__)

#it is the folder the script is in, will need to change if parent folder is different
#version = __file__.split('\\')[-2]

# Gets the path of icon image
icon_path = fr"{script_path}\pythonIcon.ico"
image = Image.open(icon_path)    # Opens the Icon 
#https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread-in-python

def sysIcon():
    systray = pystray.Icon(name="Python Macro", icon=image, title=f"Python Macro {get_version()}", menu=pystray.Menu(
        pystray.MenuItem("Quit", lambda: macro_driver.stop())
    ))
    systray.run()


def main():
    threading.Thread(target = sysIcon, daemon=True).start()

    global macro_driver
    # Create a new macro driver
    macro_driver = MacroDriver()

    # Start the macro driver
    macro_driver.start()

if __name__ == '__main__':
    main()

    """
    TODO:
        try and transition all pyautogui keyboard funtions to custom_keyboard
        add a write function to custom_keyboard


    """