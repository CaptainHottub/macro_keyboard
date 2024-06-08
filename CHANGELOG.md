# Change Log

My macro_keyboard project

All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [v2.2.121.b] - 2024-06-08

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

## [v2.2.111] - 2024-06-07

Removed unessisary comments

### Changed
- Removed unessisary comments
- chromeAudioControl and mediaTimerV2

## [v2.2.110] - 2024-06-07
 
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

## [v2.2.108] - 2024-04-22
 
chromeAudioControl is more reliable

### Changed
- I believe I made chromeAudioControl more reliable

## [v2.2.107] - 2024-04-19
 
Changed how spotify controls work

### Added

- Added a zoomin and zoomout macro for LibreOffice Draw

### Changed
- N/A

### Fixed
- N/A

## [v2.2.105] - 2024-04-19
 
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


## [v2.2.101] - 2024-04-18
 
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