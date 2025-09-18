Fix any bugs introduced when using Wayland on linux

It looks like PyWinCtl does what I need for. It has Ctypes stuff for linux      :https://pywinctl.readthedocs.io/en/latest/?badge=latest#window-features
Pyautogui works in linux, so does pynput

https://stackoverflow.com/questions/43540782/python-use-different-function-depending-on-os
https://stackoverflow.com/questions/791098/how-to-offer-platform-specific-implementations-of-a-module

fix the azure stuff.
Make a class for that.

Take custom_keyboard and make it windows specific, and have functions for SendInput() and keybd_event(). Some apps respond to one and not the other.


Make ReadMe Proper

Add a requirements file, use pipreqs to make it.  
Use the command below to install the needed packages.   
pip install -r requirements.txt

If you want to use the Text To Speech Macro you will need to setup a Azure Speech resource.   
Quickstart guide: https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/get-started-text-to-speech?tabs=windows%2Cterminal&pivots=programming-language-python   

