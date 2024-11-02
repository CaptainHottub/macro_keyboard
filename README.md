
# macro_keyboard

13-Key USB Macro Keyboard using the [KB2040 Kee Boar Driver][KB2040]

![alt text](https://github.com/CaptainHottub/macro_keyboard/blob/master/Images/macro_keyboard.jpg?raw=true)
## Features
- The KB2040 MC communicates with the Python driver that runs on your computer
- The Python driver is fully customizable with the capability for application specific macros
- The Python driver allows for special scripts and complex macros. Anything you can think of.
- 3x4 Grid with 12 keys and 1 mode button
- 2 Rotary encoders with buttons
- 15 Addressable RGB LED backlights.
- South Facing LED and sockets
- KAILH hot swap sockets
- Unlimited layers and key combinations

## Getting Started
macro_keyboard V2.2x was designed to use the [Adafruit KB2040 - RP2040 Kee Boar Driver][KB2040], which has the same shape as the Arduino Pro Micro, so you could use any Arduino Pro Micro shaped MC in this macro_keyboard.
> If you use a different micro controller, you will have to change the pins in the MC code.

The KB2040 currently runs [CircuitPython](https://circuitpython.org/) version 8.2.9, but should work with anything newer.

#### Dependencies
If you are on Linux want to use the Media Controller macros you will you will need to install this package:
`sudo apt install libdbus-1-dev`

### KB2040 Setup
You will need to install CircuitPython on your KB2040 and to do so, follow Adafruit's excellent guide how to do exactly that: https://learn.adafruit.com/adafruit-kb2040/circuitpython

Once you get CircuitPython running on your KB2040, you will need to add a couple of libraries to it.
The Libraries that you will need are: 
- adafruit_hid
- adafruit_ticks.mpy
- neopixel.mpy

You can find them and the instructions to install them in the **CircuitPython Libraries** section of Adafruits KB2040 guide: https://learn.adafruit.com/adafruit-kb2040/circuitpython-libraries
You will find the libraries in the [**CircuitPython Library Bundle**](https://circuitpython.org/libraries)

Move the `code.py` file found in `src/Microcontroller/` onto the KB2040, then the KB2040 should do a soft reboot and start running that code.

### Python Driver Setup
The driver is a python script that connects to the comport that the KB2040 is connected to when plugged in via USB.  Once it connects to the comport, it waits for a "message" from the KB2040.  The "message" is sent when a button is released or an encoder changes position by turning.

The driver use [Python 3.12](https://www.python.org/downloads/)  or newer. Instruction on how to install Python can be found here: https://wiki.python.org/moin/BeginnersGuide/Download

To download the driver you can clone the repo or download a .zip of it:

    git clone https://github.com/CaptainHottub/macro_keyboard.git

You will need to install all the Python libraries listed in the `requirements.txt` file. Install using:

    pip install -r requirements.txt
In the `config.yaml` file you can find config options for:
Logging level, (INFO or DEBUG)

    logging: True 
    logging_level: DEBUG

Log Folder

    enter code log_folder: True
    log_folder_path: "" # The direct path
    log_folder_path_relative: "/logs" # relative from /macro_keyboard/

System Tray Icon

    system_tray_icon: True  
    # The direct path
    system_tray_icon_image_path: ""  
    # relative from /macro_keyboard/
    system_tray_icon_image_path_relative: "/Images/pythonIcon.ico"  

Connection Notification

    connected_notification: True  
    # in seconds
    notification_time: 2

Spotify auto start

    spotify_auto_start: False

Everything in the `config.yaml` file can be changed, you can add or remove whatever you want.

To run it you need to run the `macro_driver.py` in a terminal:

    python -u "/macro_keyboard/src/Driver/macro_driver.py"

### Assembling the PCB
Soldering all the components to the PCB can be a little difficult as I did chose some pretty small components, especially the LED's and diodes.
The production Gerber zip file for the PCB is in `src/PCB/Macro_PCB_2.2.x_Production_Gerber`, which you can submit to JLCPCB to get made.
The Bill Of Material is at  `/src/macro_keyboard_BOM.csv`. Most parts can be sourced from DigiKey.

There is a `macro_keyboard.step` that should help with any questions on component orientation.

**Bottom Mount Components**
- 13 KAILH Hot Swap Sockets
- 12 Diodes
- 15 SK6812-E RGB LEDS
- 330 OHM Resistor for LED Data Pin

![alt text](https://github.com/CaptainHottub/macro_keyboard/blob/master/Images/Bottom_Mount_components.png?raw=true)
> **Pay close attention to the position of the diode and especially the LED**

![alt text](https://github.com/CaptainHottub/macro_keyboard/blob/master/Images/Propper_Orientation_for_Diode_and_LED.png?raw=true)

**Top Mount Components**
- KB2040
- 6x6mm Tactile Switch
- 2x Rotary Encoders (Is not necessary if you don't want it.)

![alt text](https://github.com/CaptainHottub/macro_keyboard/blob/master/Images/top_mount_components.png?raw=true)
If done properly any MX compatible key switch should just slide into each socket. The PCB is compatible with 3-pin and 5-pin key switches.

**Assembled PCB**

![alt text](https://github.com/CaptainHottub/macro_keyboard/blob/master/Images/assembled_PCB.png?raw=true)
You should now have a fully assembles macro_keyboard that's ready to run. :)
It just needs a case.

### 3D Printed Case
Top half of the case

![alt text](https://github.com/CaptainHottub/macro_keyboard/blob/master/Images/Top_case.png?raw=true)

The top half also serves as a plate that the keys snap into.

![alt text](https://github.com/CaptainHottub/macro_keyboard/blob/master/Images/top_case_with_assembled_PCB.png?raw=true)

The bottom case on the left is called; `Bottom_Case_with_hole_V2.stl`, and the bottom case on the left is called; `Bottom_Case_No_Hole_V2.stl`

![alt text](https://github.com/CaptainHottub/macro_keyboard/blob/master/Images/both_versions_bottom_case.png?raw=true)
The case uses 4 M3x12mm screws to secure it together, but it does support M3x10mm screws.

### Macro Examples
There are multiple macros that will work when you initially setup the driver. A couple of them are more complex then just keystrokes.
There are two groups of macro that I use the most, the first "group" is to control Spotify, the second "group" is to change and move apps across virtual desktops.

#### Spotify Macros
These macros use different code for different Operation Systems, because the Windows code wasn't compatible with Linux.
The prepacked macros involving Spotify are:

```python
####################################### Encoder 1 ########################################
match [app, encoder_data['Id'], encoder_data['Value'], layers]:
	case [_, 1, "RL", []]:	# Rotate Left
		logger.debug('VolumeDown')
		threading.Thread(target=Spotify.event_handler, args=('VolumeDown',)).start()
	case [_, 1, "RR", []]:	# Rotate Right
		logger.debug('VolumeUp')
		threading.Thread(target=Spotify.event_handler, args=('VolumeUp',)).start()
	case [_, 1, "RLB", []]:	# Rotate Left with Button
		logger.debug('Back5s')
		threading.Thread(target=Spotify.event_handler, args=('Back5s',)).start()
	case [_, 1, "RRB", []]:	# Rotate Right with Butotn
		logger.debug('Forward5s')
		threading.Thread(target=Spotify.event_handler, args=('Forward5s',)).start()

####################################### Buttons ########################################
match [app, mode, event_data['Button_id'], layers]:
	case [_, mode, 2, []]: # button 2
		logger.debug("Btn 2, no layers")
		threading.Thread(target=Spotify.press, args=()).start()
	case [_, mode, 2, [3, 4]]: # button 2 while button 3 and 4 are held
		logger.debug("Moves Spotify to the current virtual Desktop")
		threading.Thread(target=Spotify.move_spotify_window, args=('Current',)).start()    
	case [_, mode, 2, [3]]: # button 2 while button 3 is held
		logger.debug("Moves Spotify to the virtual Desktop on the left")
		threading.Thread(target=Spotify.move_spotify_window, args=('Left',)).start()    
	case [_, mode, 2, [4]]: # button 2 while button 4 is held
		logger.debug("Moves Spotify to the virtual Desktop on the right")
		threading.Thread(target=Spotify.move_spotify_window, args=('Right',)).start()   
	case [_, mode, 2, [1]]: # button 2 while button 1 is held
		logger.debug("Btn 2 and btn 1 as layer")
		threading.Thread(target=FireFox.press, args=()).start()
```
The macro I use the most is Spotify.press() which is attached to Button 2.
It works exactly like Apple's EarPods or there AirPods, where 1 press will play/pause, 2 presses will skip to the next song and 3 presses goes to the previous song.
On Linux it uses the `org.mpris.MediaPlayer2`  dbus interface to control media players.
On Windows it uses `pywinauto`  to connect to Spotify and send keyboard inputs.



## Inspiration
All of this was inspired by Ryan Bates and his [Macro Keyboard Video][video-inspiration]
[Website][retrobuilds2]


## License, Copyright, and Legal
All software and hardware designs in this repository are licensed under the [Creative Commons Attribution-NonCommercial 4.0 International][cc-by-nc] license.
[![CC BY-NC 4.0][cc-by-nc-image]][cc-by-nc]

[cc-by-nc]: https://creativecommons.org/licenses/by-nc/4.0/
[cc-by-nc-image]: https://licensebuttons.net/l/by-nc/4.0/88x31.png


[retrobuilds]: http://www.retrobuiltgames.com/the-build-page/macro-keyboard-v2-0/ 
[retrobuilds2]: https://github.com/retrobuiltRyan/MacroKeyboardV2
[video-inspiration]: https://www.youtube.com/watch?v=IDlcxLQ1SbY
[KB2040]: https://www.adafruit.com/product/5302
