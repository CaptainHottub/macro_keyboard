# Change Log
All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).
 
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