from setup import logger, send_notification
import sys
from macro_driver import MacroDriver
import macros
import time
import _linux_macros as lnm

import serial.tools.list_ports


import contextlib
import pywinauto
import pyautogui
import pyperclip
from PIL import ImageGrab
import pytesseract
from pynput import mouse, keyboard

import pyclip

"""
This will be a wrapper for 

Event_handler in macro_driver, where I can put in specific buttons and layers so i can test stuff before my ssd arrives


todo that I will have to rewrite event_handler and macros and encoders, so self.app, self.mode, self.button, self.layers is passed through and not a global var in the class
"""
def _perform_hotkey(hotkey):
    args = hotkey
    print(repr(hotkey))
    pyautogui.hotkey(hotkey)
    #logger.debug(f"perform_hotkey {hotkey = }")
    #raise NotImplementedError
    #custom_keyboard.hotkey(*hotkey)

def msgparser(msg):
    """
    This parses the message sent by the microcontroller to something useable
    I am quite impressed on how compact this is.

    Args:
        msg (str): A string of Binary

    Returns:
        button_name: Name of the button, str if Mode, or encoders, int for the rest
        event_type: What type of event it is as a str
        layers_int: List of layers
    """
    # defines button names
    button_names = {
        0: "Mode",
        14: "Encoder1",
        15: "Encoder2"}
    
    # defines event names
    events_names = {
        0: "btnPress",     # 0000, 1
        1: "btnRelease",   # 0001, 2
        2: "RL",           # 0010, 3      rotary left w/o button
        3: "RR",           # 0011, 4      rotary right w/o button
        6: "RLB",          # 0110, 6      rotary left w/ button
        7: "RRB"           # 0111, 7      rotary right w/ button
        }

    logger.debug("Parsing message")

    # for somereason, in linux, on the first readline the value is something like: "\x1b]0;🐍code.py | 8.2.9\x1b\\ +msg"
    # this one line fixes that
    msg = msg.split('\\')[-1]


    # splits the string every 4th character
    *layers_int, event_int, button_int = [int(msg[i:i+4], 2) 
                                            for i in range(0, len(msg), 4)]

    # renames the buttons if the key is valid, if not returns button_int
    button_name: str | int = button_names.get(button_int, button_int)
    
    # gets the event type
    event_type: str = events_names[event_int]
    
    layers = layers_int[::-1]
    if len(layers) > 0 and not layers[-1]:
        layers[-1] = "Mode"

    return button_name, event_type, layers

def _Image_to_text2():
    """
    Okay so in this version, if you're linux distro is using spectacle to take screenshots  you will have to configure and make it save to clipboard

    Presses Win Shift PrtSc to open spectacle mode, waits for mouse release then does tesseract OCR
    Press Ctrl V to paste text
    It works but spectacle takes some time too launch
    """
    
    m = mouse.Controller()
    k = keyboard.Controller()

    def on_release(key):
        if key == keyboard.Key.esc:
            logger.debug('esc pressed and released')
            # Stop listener and the func
            m.click(mouse.Button.left,1)
            return False    
        
    def on_click(x, y, button, pressed):
        if not pressed:
            # Stop listener
            k.press(keyboard.Key.enter)
            k.release(keyboard.Key.enter)
            
            return False
    
    m.click(mouse.Button.left,1)
    
    time.sleep(0.2)
    _perform_hotkey(['win', 'shift', 'prtsc'])
    
    keyboard_listener = keyboard.Listener(
        on_release=on_release)

    time.sleep(0.2)

    keyboard_listener.start()

    # Collect events until released # is used to block the code until the left mouse button is released
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()
        
    time.sleep(0.1)

    keyboard_listener.stop()

    time.sleep(0.3)
    img = ImageGrab.grabclipboard()
    #grabs the image from clipboard and converts the image to text.
    text = pytesseract.image_to_string(img)
    text = text.replace('\x0c', '')
    pyclip.copy(text)
    logger.debug("imt has finished")


def main():
    macro_driver = MacroDriver()
    print("Whatever you input next will be redirected to macro_driver.Event_handler()")
    
    while True:
        print("\nLayout is: event_type, button, layers")
        print('Example: Button, 2, []\n')

        cmd_to_send = input("What is your input: ")
        cmd_to_send = cmd_to_send.replace(' ','')
        event_type, button, *layers = cmd_to_send.split(',')
        button = int(button)
        
        if layers == ['[]']:
            layers = []
        else: 
            temp_list = []
            layers[0] = layers[0][1:]
            layers[-1] = layers[-1][:-1]

            for i in layers:
                if i not in ['Mode', 'mode']:
                    i = int(i)
                temp_list.append(i)
                
            layers = temp_list
            
        macro_driver.Event_handler(button, event_type, layers)

def tester():
    # Spotify = macros.SpotifyController()
    # app  = ''
    # macros.change_desktop('left', app)
    # time.sleep(1)
    # macros.change_desktop('right', app)
                
                
    #Spotify.move_spotify_window_to_current_desktop()      
    # lnm._moveFocusedAppAccrossDesktops('right')      
    # time.sleep(1)
    # lnm._moveFocusedAppAccrossDesktops('left')  
    
    _Image_to_text2()  


if __name__ == '__main__':
    
    plat = sys.platform.lower()
    if plat[:5] == 'linux':
        logger.warning("Some features may not work")
        #toaster.show_toast("Warning", "Some features may not work on Linux", duration=2, threaded=True)
        send_notification(title='Warning', msg='Some features may not work on Linux')

    #main()
    tester()
