This is my macro keyboard project. It uses a Python script that acts as a driver.

It receives text from the microcontroller over USB serial and it executes macros and some more complex stuff.

I'm doing this instead of using QMK or having the microcontroller send keystrokes because it allows me to do some more complex things.

One of these macros uses the Tesseract OCR module in Python. I press the button it's assigned to on the macro and it takes a screenshot and outputs the text in it to my clipboard, so I can paste it immediately.

Another one uses Microsoft Azures Text To Speech API to read the text I selected.

MacroV3.1.2.py is the current version.

This is still a work in progress, expect this repository to change very soon. 	

Currently, the V1 through V3 just means the Driver version.	

I am not sure how I'm going to name things, I think I'll move and rename verything from V1 to V3 to a V1 Folder and have it named as Driver V1.3.1.2 or something.	

I imagine that the PCB im going to design will be named V2.0.001, same goes for the driver.	

V1 through V3 is using Ryan Bates Macro Keyboard Ver2.0 design.  
http://www.retrobuiltgames.com/the-build-page/macro-keyboard-v2-0/  
I am planning on making my own varient of it, that will use Kailh Hot-Swap PCB sockets:   
https://www.amazon.ca/Hot-swap-CPG151101S11-Mechanical-Keyboard-Accessories/dp/B0BVH3SVHW   

I hava macro that will play/pause, next song and previous song for spotify. It works by just pressing the media key.    
There is an issue with this approach and it is that Google Chrome and possibly other chromium based browsers interact with media keys too.  
So pressing the PlayPause media key will playPause spotify and whatever video you may have open in a webbrowser. To stop Google Chromes interaction with media keys 
you need to disable it in chrome://flags/#hardware-media-key-handling

WHAT I WANT TO DO:  
Add a requirements file, use pipreqs to make it.  
Update to python 3.12

I need to remove lines 280 to 291 in tools.py

Will put a settings.txt file in the future that will allow you to define multiple things. 
Example:  
  logging==True   
  log_folder_path=="C:\User\Desktop"  
  system_tray_icon==True  
  system_tray_icon_image_path=="C:\Users\User\Desktop\macro_keyboard-master\MacroV3\v3.1\pythonIcon.ico"  

  connected_notification==True  
  access_denied_notification==True  
  disconnected_notification==True 

Make ReadMe Proper


Use the command below to install the needed packages.   
pip install -r requirements.txt

If you want to use the Text To Speech Macro you will need to setup a Azure Speech resource.   
Quickstart guide: https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/get-started-text-to-speech?tabs=windows%2Cterminal&pivots=programming-language-python   
I will need to figure out a better way to store and get the speech_key and speech_region for it.    
Currently you needd to put that in a file and put the file path in line 45 and 280 in tools.py    

You also need to put a path for a log folder at line 12 in logger.py    
This needs to be made better. 
