# Change Log

My macro_keyboard project

All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
<!-- and this project adheres to [Semantic Versioning](http://semver.org/). -->



## [2.3.009] - 2025-9-18
- Added a Soundboard Functionality
- Temporary fix for recursion limit crash
- Temporaraly disabled any function that gets window/app info, Wayland breaks alot of that.
- Slight update to requirments.txt


## [2.3.007] - 2024-11-02
- Added a new logging level called "trace", use only to show the most detailed info
- Implemented Spotify.move_spotify_window()
- Added pywin32==308 to the requirements.txt, its for Windows
- Updated README.md
- Added images for 3d printed case

## [2.3.005] - 2024-11-01
_MasterMediaController() now uses mpris2 package

## [2.3.004] - 2024-10-31
New Top Case that also acts as the plate for the keyswithes
Updated Photos

### Changed
- Changed the way the "focused_window_title" is aquired on linux, this should now work for factorio

## [2.3.003] - 2024-08-30
Driver shoudn't crash when Microcontroller is unpluged

## [2.3.002] - 2024-07-29
was messing with asyncio on microcontroller for the layer leds, It doesnt seem to run asynchronisly

### Changed
- lightshow when microcontrller boots

## [2.3.001] - 2024-07-14
IT SHOULD WORK THE SAME
You can now send text or json to the microcontroller.
Big changes to MacroDriver and the microcontroller code,
An LED now lights up when the pause state is true 

### Changed
- Changed the structure of MacroDriver:
- Moved Button_handler and Encoder_handler outside of MacroDriver

### Added
- You can now send text or json to the microcontroller.

## [2.2.137.b] - 2024-07-04
Improved Media Controllers for firefox and spotify.
Semi-update

### Changed
- Spotify and firefox controllers grab from the master controller.
- This would probably work with chrome too

### Added
- A MasterMediaController class, that has the press, and envent_handler stuff in it

## [2.2.136.b] - 2024-06-29
Requirements file
A media controller for FireFox, and TTS works

### Changed
- Modified the code that gets the app name, will have to make it better.
- Pyclip is replacing Pyperclip, because Pyperclip wasn't in macros, only in that file. IDK why
- Azure TTS now works on linux.

### Added
- Requirements file
- A media controller for FireFox
- spotify_auto_start setting to config. when 1, spotify will automaticaly start if you try and interact with it.
- libreOffice_font_size_up() and libreOffice_font_size_down(). does exactly what its called

## [2.2.135.b] - 2024-06-27
I belive most of the macros will work on linux.

### Changed
- The Azure TTS only works on Windows, I cant get it to work right now.
- ButtonMode() now prints in the console instead of creating a window, it was crashing on the second time being pressed on linux (this is a temp solution) 


## [2.2.132.b] - 2024-06-17

If spotify isnt running it will start, when _SpotifyController is called


## [2.2.131.b] - 2024-06-13

Major changes to file structure

Tools.py moved to macros.py
and the os specific function got moved to there own files.
move_desktop and spotify controller are the only functions that are currently cross platform
_Image_to_text2 now works on linux.

Azure speechsdk is broken for some reason

### Changed
- Getting the focused_window name is more reliable


## [2.2.125.b] - 2024-06-09

### Added
- Added some logs when certain things are initialized

### Changed
- The System Tray Icon should now show the full version.

## [2.2.124.b] - 2024-06-09

It should be easier to test macros now.
added testing.py, that will ask for an input and it will send said input to MacroDriver.Event_handler()

### Added
- testing.py

### Changed
- button, event_type, layers and app are no longer globals variables
- tools.change_desktop() should now be faster


## [2.2.123.b] - 2024-06-08

It now works on linux and windows.
There are still some bugs, like the Azure speech stuff doesnt work


## [2.2.121.b] - 2024-06-08

First port to linux

### Added
- a config file: config.yml
- media_controller.py

### Changed
- A lot of stuff got changed.
- main.py got merged with macro_driver.py
- logger.py was renamed to setup.py
- the media controllers got moved to media_controller.py
- The Azure speech stuff will not work on linus due to a big.

## [2.2.111] - 2024-06-07

Removed unessisary comments

### Changed
- Removed unessisary comments
- chromeAudioControl and mediaTimerV2

## [2.2.110] - 2024-06-07
 
Brainstorming in TODO
Minor changes

### Added

- Youtube Music Controller Class
- New function that sets the desktop as focused

### Changed
- Changed the match case statment variable positions in Button_handlerV3
- get_focused() returns the handle of that window.

- chromeAudioControl has been updated to a ChromeController class
- moveAppAccrossDesktops() only accepts window handles.
- Removed the unecisary Ctypes stuff in tools. (except for the VDA stuff)
- Modified get_processes()
- Removed hwndGetter().

## [2.2.108] - 2024-04-22
 
chromeAudioControl is more reliable

### Changed
- I believe I made chromeAudioControl more reliable

## [2.2.107] - 2024-04-19
 
Changed how spotify controls work

### Added

- Added a zoomin and zoomout macro for LibreOffice Draw

### Changed
- N/A

### Fixed
- N/A

## [2.2.105] - 2024-04-19
 
Changed how spotify controls work

### Added

- SpotifyController Class
  All the spotify specific controlls are now in that class.
  I haven't written any documentation for it yet.

- MediaTimer is a class now
  It works the same as before.
  Again, haven't written documentation yet

- The taskbar icon and the logger now get the version from the CHANGELOG.md file

### Changed
- Removed most of the VirtualDesktopAccessor.dll Functions.
 
- Commented out spotifyControl and moveSpotifyAccrossDesktops functionns

### Fixed
- N/A


## [2.2.101] - 2024-04-18
 
First CHANGELOG commit
 
### Added

- moveAppAccrossDesktops and moveSpotifyAccrossDesktops were added
  Now you can move Spotify across desktops, instead of just to the current one, I also works for the focused app.

- launchApp
  It lets you input the name of an app or the path to it as a argument and it will try and launch it.
  Its currently only used to launch Spotify.

### Changed
- Commented out most of the VirtualDesktopAccessor.dll Functions.
 
- In mediaTimerV2, the timer function now calls runAfterTimer, and that calls the function you want

- spotifyControl, will now launch spotify if it is not running
### Fixed
- N/A