Move all the ctypes stuff over to pywin, win32gui and that stuff

I want to move over to Linux From Windows, so I will have to re write a bunch of stuff to be compatible with it.
It looks like PyWinCtl does what I need for. It has Ctypes stuff for linux      :https://pywinctl.readthedocs.io/en/latest/?badge=latest#window-features
Pyautogui works in linux, so does pynput

So It doesn't look like I can use pywinauto to connect to an app and send keystrokes to it.




Add a requirements file, use pipreqs to make it.  
Will put a settings.txt file in the future that will allow you to define multiple things. 
Example:  
    logging==True   
    logging_level==2
    log_folder_path=="C:\User\Desktop"  
    system_tray_icon==True  
    system_tray_icon_image_path=="C:\Users\User\Desktop\macro_keyboard-master\MacroV3\v3.1\pythonIcon.ico"  

    connected_notification==True  
    access_denied_notification==True  
    disconnected_notification==True
    notofication_time== 2



Make ReadMe Proper


Use the command below to install the needed packages.   
pip install -r requirements.txt

If you want to use the Text To Speech Macro you will need to setup a Azure Speech resource.   
Quickstart guide: https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/get-started-text-to-speech?tabs=windows%2Cterminal&pivots=programming-language-python   
I will need to figure out a better way to store and get the speech_key and speech_region for it.    
Currently you needd to put that in a file and put the file path in line 45 and 280 in tools.py    

You also need to put a path for a log folder at line 12 in logger.py    
This needs to be made better. 