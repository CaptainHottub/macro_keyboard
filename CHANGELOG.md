# Change Log

My macro_keyboard project

All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

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