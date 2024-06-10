I want to move over to Linux From Windows, so I will have to re write a bunch of stuff to be compatible with it.

It looks like PyWinCtl does what I need for. It has Ctypes stuff for linux      :https://pywinctl.readthedocs.io/en/latest/?badge=latest#window-features
Pyautogui works in linux, so does pynput

Brainstorming some major structure changes:
macro_driver.py -> driver.py
tools.py -> macros.py

Take the windows specific function from tools.py and media_controller.py and put in _utils_win32.py
then do the same for linuxs specific fonctions and put them in _utils_posix.py
then you can use platformModule, 
 
in macros you can do:  # you would have to create an instance of that class when you first load macros.py
Spotify = platformModule.SpotifyController()

def Spotify_press():
    Spotify.press()
def Spotify_event_handler():
    Spotify.event_handler()

then at the start of macros.py do:
if sys.platform == 'win32':
    from _utils_win32 import SpotifyController
    from _utils_win32 import ChromeController
    from _utils_win32 import YTMusicController
    from _utils_win32 import change_desktop
elif sys.platform == 'linux':
    from _utils_posix import SpotifyController
    from _utils_linux import ChromeController
    from _utils_linux import YTMusicController
    from _utils_linux import change_desktop

ORRRR
do like Pyautogui with platformModule   line 535 in __init__
# The platformModule is where we reference the platform-specific functions.
if sys.platform == "win32":
    from . import _utils_win32 as platformModule
elif sys.platform == "Linux":
    from . import _utils_linux as platformModule
else:
    raise NotImplementedError("Your platform (%s) is not supported by PyAutoGUI." % (platform.system()))

I like platformModule because instead of:
_utils_linux.SpotifyController, its platformModule.SpotifyController

also maybe make a main controller class like this
class Controller():
    def __init__(self):
        self.mediaTimer = MediaTimer()
    
    
    def event_handler(self, event):

        print(event)
        

    def press(self):
        if result := self.mediaTimer.press_button():
            logger.debug(result)
            self.event_handler(result)
        


https://stackoverflow.com/questions/43540782/python-use-different-function-depending-on-os
https://stackoverflow.com/questions/791098/how-to-offer-platform-specific-implementations-of-a-module

fix the azure stuff.




Make ReadMe Proper

Add a requirements file, use pipreqs to make it.  
Use the command below to install the needed packages.   
pip install -r requirements.txt

If you want to use the Text To Speech Macro you will need to setup a Azure Speech resource.   
Quickstart guide: https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/get-started-text-to-speech?tabs=windows%2Cterminal&pivots=programming-language-python   

