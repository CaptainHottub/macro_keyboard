# macro_keyboard

13-Key USB Macro Keyboard using the [KB2040 Kee Boar Driver](https://www.adafruit.com/product/5302)

[![alt text](https://github.com/CaptainHottub/macro_keyboard/raw/master/Images/macro_keyboard.jpg?raw=true)](https://github.com/CaptainHottub/macro_keyboard/blob/master/Images/macro_keyboard.jpg?raw=true)

## Features

* The KB2040 MC communicates with the Python driver that runs on your computer
* **Wayland Support:** Optimized for Linux (Fedora/KDE) with Wayland support.
* 3x4 Grid with 12 keys and 1 mode button
* 2 Rotary encoders with buttons
* 15 Addressable RGB LED backlights.
* South Facing LED and sockets
* KAILH hot swap sockets

## Getting Started

macro_keyboard V2.4x was designed to use the [Adafruit KB2040 - RP2040 Kee Boar Driver](https://www.adafruit.com/product/5302).

> If you use a different micro controller, you will have to change the pins in the MC code.

The KB2040 currently runs [CircuitPython](https://circuitpython.org/) version 8.2.9 or newer.

#### Dependencies

**Linux (Fedora/KDE Wayland):**
The driver uses `qdbus` for native desktop switching on KDE Plasma.
If you require advanced window manipulation, we recommend installing `kdotool` (a drop-in replacement for `xdotool` on Wayland).

### KB2040 Setup

Follow Adafruit's guide to install CircuitPython: [https://learn.adafruit.com/adafruit-kb2040/circuitpython](https://learn.adafruit.com/adafruit-kb2040/circuitpython)

Install these libraries from the [**CircuitPython Library Bundle**](https://circuitpython.org/libraries):
* adafruit_hid
* adafruit_ticks.mpy
* neopixel.mpy

Move the `code.py` file found in `src/Microcontroller/` onto the KB2040.

### Python Driver Setup

The driver uses [Python 3.12](https://www.python.org/downloads/) or newer.

1. Clone the repo:
   ```bash
   git clone [https://github.com/CaptainHottub/macro_keyboard.git](https://github.com/CaptainHottub/macro_keyboard.git)
2.  Install Python dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure the driver:**
    Edit `config.yml`. You can now use `~` to reference your home directory safely.

    ```yaml
    paths:
      sounds: "~/Documents/soundboard_audios" # Uses your home dir automatically
    ```

4.  Run the driver:

    ```bash
    python -u "src/Driver/driver_main.py"
    ```

-----

## User Macros (The Sandbox)

**New in v2.4:** You don't need to edit the complex driver code to add your own macros\!
Open `src/Driver/user_macros.py` and write your own Python code using the simple `@register` tool.

### How to add a macro:

1.  Open `user_macros.py`.
2.  Import the tools: `from macro_handlers import register, user_log, play_user_sound`.
3.  Write a function and decorate it.

**Example: Open VS Code**

```python
@register(button=5, app="Visual Studio Code")
def run_my_code():
    user_log("Running Code...")
    macros.perform_hotkey(['ctrl', 'alt', 'n'])
```

**Example: Play a Sound**

```python
@register(button=6, layers=('Mode',))
def victory_sound():
    play_user_sound("victory.mp3") # Plays from your configured sound folder
```

**Example: Encoder Knob**

```python
from macro_handlers import register_encoder

@register_encoder(encoder_id=1, action='RR') # Rotate Right
def volume_up():
    macros.SpotifyController().event_handler('VolumeUp')
```

-----

### Assembling the PCB

The production Gerber zip file is in `src/PCB/Macro_PCB_2.2.x_Production_Gerber`.
The Bill Of Material is at `/src/macro_keyboard_BOM.csv`.

**Bottom Mount Components**

  * 13 KAILH Hot Swap Sockets
  * 12 Diodes (Pay attention to orientation\!)
  * 15 SK6812-E RGB LEDS
  * 330 OHM Resistor

    ![alt text](https://github.com/CaptainHottub/macro_keyboard/blob/master/Images/Bottom_Mount_components.png?raw=true)
    > **Pay close attention to the position of the diode and especially the LED**

    ![alt text](https://github.com/CaptainHottub/macro_keyboard/blob/master/Images/Propper_Orientation_for_Diode_and_LED.png?raw=true)

**Top Mount Components**

  * KB2040
  * 6x6mm Tactile Switch
  * 2x Rotary Encoders

    ![alt text](https://github.com/CaptainHottub/macro_keyboard/blob/master/Images/top_mount_components.png?raw=true)


### 3D Printed Case

The `Case/` folder contains STLs for the case.

  * **Top Case:** Acts as the plate for key switches.

    ![alt text](https://github.com/CaptainHottub/macro_keyboard/blob/master/Images/Top_case.png?raw=true)

  * **Bottom Case:** Two versions available (with and without reset hole).
  

    ![alt text](https://github.com/CaptainHottub/macro_keyboard/blob/master/Images/both_versions_bottom_case.png?raw=true)
    > **Left: `Bottom_Case_with_hole_V2.stl`    
    Right: `Bottom_Case_No_Hole_V2.stl`**

  * Uses 4 M3x12mm or M3x10mm screws.


    The top half also serves as a plate that the keys snap into.

    ![alt text](https://github.com/CaptainHottub/macro_keyboard/blob/master/Images/top_case_with_assembled_PCB.png?raw=true)




## Inspiration

Inspired by Ryan Bates and his [Macro Keyboard Video](https://www.youtube.com/watch?v=IDlcxLQ1SbY).


## License, Copyright, and Legal
All software and hardware designs in this repository are licensed under the [Creative Commons Attribution-NonCommercial 4.0 International][cc-by-nc] license.

[![CC BY-NC 4.0][cc-by-nc-image]][cc-by-nc]

[cc-by-nc]: https://creativecommons.org/licenses/by-nc/4.0/
[cc-by-nc-image]: https://licensebuttons.net/l/by-nc/4.0/88x31.png
