This is my macro keyboard project. It uses a Python script that acts as a driver.

![alt text](https://github.com/CaptainHottub/macro_keyboard/blob/master/Images/macro_keyboard.jpg?raw=true)

Hi UBCV, if you were wondering, this is one of Taylor McLaughlin's git hub repositories.

It receives text from the microcontroller over USB serial and it executes macros and some more complex stuff.

I'm doing this instead of using QMK or having the microcontroller send keystrokes because it allows me to do some more complex things.
One of these macros uses the Tesseract OCR module in Python. I press the button it's assigned to on the macro and it takes a screenshot and outputs the text in it to my clipboard, so I can paste it immediately.
Another one uses Microsoft Azures Text To Speech API to read the text I highlight.
I have one macro that moves Spotify to the current desktop.

This is a work in progress.

All of this was inspired by Ryan Bates and his [Macro Keyboard Video][video-inspiration]

[Website][retrobuilds]


![alt text](https://github.com/CaptainHottub/macro_keyboard/blob/master/Images/pcb.jpg?raw=true)

I  have one button that works like the button on the old wired headphones from Apple.
1 press will play/ pause, 2 presses will go to the next song, and 3 presses will got to the previous song.

previous versions of it would use the play pause virtual key, and a downside is Google Chrome and possibly other chromium-based browsers interact with it too. To stop Google Chromes interaction with media keys you need to disable a flag: chrome://flags/#hardware-media-key-handling
But on the current version, I use a different method to interact with Spotify that doesn't use the play pause virtual key.

I have added rotary encoders to the PCB and the possibility of using layers.
Buttons that I hold down for long enough act like layers, they work similarly to the shift key, and how you get 3 without it and # with it.
Or like the fn key on laptops.

The way I wrote the microcontroller code is that any key can be a layer and the only limit to how many you can have presses is the number of buttons connected to the microcontroller.



This work is licensed under a
[Creative Commons Attribution-NonCommercial 4.0 International License][cc-by-nc].

[![CC BY-NC 4.0][cc-by-nc-image]][cc-by-nc]


[cc-by-nc]: https://creativecommons.org/licenses/by-nc/4.0/
[cc-by-nc-image]: https://licensebuttons.net/l/by-nc/4.0/88x31.png

[retrobuilds]: http://www.retrobuiltgames.com/the-build-page/macro-keyboard-v2-0/ 
[video-inspiration]: https://www.youtube.com/watch?v=IDlcxLQ1SbY