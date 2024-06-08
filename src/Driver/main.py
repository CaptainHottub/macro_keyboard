#from logger import logger
from macro_driver import MacroDriver

import pystray
import os
from PIL import Image
import threading

"""
This should work with linux, havent tried it yet
"""


def get_version(file_dir)-> str:
    """Looks through the CHANGELOG.md file for the version number

    Returns:
        str: The version number
    """
    changelog_path = file_dir+'/CHANGELOG.md'
    
    try:
        string_with_version_in_it = ''
        with open(changelog_path,'r') as file:
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


def sysIcon():
    """
    The icon for the widget will live in # '/macro_keyboard/Images/pythonIcon.ico'
    
    """ 
    script_path = os.path.dirname(__file__)
    file_directory_temp = script_path.split('\\')[0:-2]
    
    file_dir = '/'.join(file_directory_temp)
    
    icon_path = fr"{file_dir}/Images/pythonIcon.ico"
    image = Image.open(icon_path)

    version = get_version(file_dir)
    
    systray = pystray.Icon(name="Python Macro", icon=image, title=f"Python Macro {version}", menu=pystray.Menu(
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