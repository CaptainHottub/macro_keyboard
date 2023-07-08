This is my macro keyboard project, V1 through V3 is using Ryan Bates Macro Keyboard Ver2.0 design.  
http://www.retrobuiltgames.com/the-build-page/macro-keyboard-v2-0/  
This Summer I am planning on making my own varient of it, what will use Kailh Hot-Swap PCB sockets:   
https://www.amazon.ca/Hot-swap-CPG151101S11-Mechanical-Keyboard-Accessories/dp/B0BVH3SVHW   

MacroV3.1.py is the current version.

V3.1 or V3.2 wont run because I didn't update the Autoit package. I will fix it when I can.

I hava macro that will play/pause, next song and previous song for spotify. It works by just pressing the media key.    
There is an issue with this approach and it is that Google Chrome and possibly other chromium based browsers interact with media keys too.  
So pressing the PlayPause media key will playPause spotify and whatever video you may have open in a webbrowser. To stop Google Chromes interaction with media keys 
you need to disable it in chrome://flags/#hardware-media-key-handling

WHAT I WANT TO DO:  
Add a requirements file, use pipreqs to make it.  
Update to python 3.11 

I need to remove lines 280 to 291 in tools.py

Will put a settings.txt file in the future that will allow you to define multiple things. 
Example:  
  logging==True   
  log_folder_path=="C:\User\Desktop"  
  system_tray_icon==True  
  system_tray_icon_image_path=="C:\Users\Taylor\Desktop\macro_keyboard-master\MacroV3\v3.1\pythonIcon.ico"  

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
