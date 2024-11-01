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
- Unlimited layers and key combinations (not literally, more like $12^{12}$)

## Getting Started
macro_keyboard V2.2x was designed to use the [Adafruit KB2040 - RP2040 Kee Boar Driver][KB2040], which has the same shape as the Arduino Pro Micro, so you could use any Arduino Pro Micro shaped MC in this macro_keyboard.
> If you use a different micro controller, you will have to change the pins in the MC code.

The KB2040 currently runs [CircuitPython](https://circuitpython.org/) version 8.2.9, but should work with anything newer.

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
