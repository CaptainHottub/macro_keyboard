"""
USER MACROS
-----------
"""
from macro_handlers import logger, button_register, register_encoder, play_user_sound, Spotify
import macros
import time
"""
# -- Examples, not expected to run --
# Example 1: Overwrite Button 5 to print "Hello World"
@button_register(button=20, mode=3)
def hello_world():
    print("Hello Engineering World!")

# Example 2: Run a hotkey for a specific app
@button_register(button=21, app="Discord")
def mute_discord():
    # Ctrl + Shift + M is often mute
    macros.perform_hotkey(['ctrl', 'shift', 'm'])
    

# --- Example: Encoder ---
# "When I turn the left knob (1) to the right ('CW'), play a sound"
@register_encoder(encoder_id=1, action='CW', mode=3)
def crank_it_up():
    user_log("Cranking the volume!")
    play_user_sound("victory.mp3")



Button Layout
     +----+----+----+----+
     |  1 |  2 |  3 |  4 |
     +----+----+----+----+
     |  5 |  6 |  7 |  8 |
+----+----+----+----+----+
|mode|  9 | 10 | 11 | 12 |
+----+----+----+----+----+

"""

# -- Global Media Controls --

# @button_register(button=_, app="",  layers=('Mode',))
# def x():
#     logger.debug("Soundboard: x")


# -------------------- Standard Button Controls --------------------

# Media Control with Layers (Spotify window movement)

@button_register(button=2,  layers=('3', '4'))
def sp_mv_current_desktop():
    logger.debug("Spotify: Move to current desktop")
    Spotify.move_spotify_window('Current')
    
@button_register(button=2,  layers=('3',))
def sp_mv_left_desktop():
    logger.debug("Spotify: Move to current desktop")
    Spotify.move_spotify_window('Left')
    
@button_register(button=2,  layers=('4',))
def sp_mv_right_desktop():
    logger.debug("Spotify: Move to current desktop")
    Spotify.move_spotify_window('Right')
            
# Any App + Any Mode + Button + Specific Layers

@button_register(button=1, layers=('3',))
def mv_app_to_desktop_left(hwnd):
    logger.debug("Move focused window to desktop left")
    macros.moveAppAccrossDesktops(hwnd, 'Left')

@button_register(button=1, layers=('4',))
def mv_app_to_desktop_right(hwnd):
    logger.debug("Move focused window to desktop right")
    macros.moveAppAccrossDesktops(hwnd, 'Right')

# @button_register(button=2, layers=('1',))
# def firefox_press():
#     logger.debug("Open FireFox")
#     FireFox.press()



# Any App + Any Mode + Button Only (lowest priority)
@button_register(button=3)
def mv_desktop_left(app):
# case (3, _, _, []):
    logger.debug("Change desktop left")
    macros.change_desktop('left', app)
    
@button_register(button=4)
def mv_desktop_right(app):    
    logger.debug("Change desktop right")
    macros.change_desktop('right', app)

@button_register(button=7, app="Google Sheets")
def sheets_transpose_selected():    
    logger.debug("Transposes the selected are in google sheets")
    macros.sheets_transpose_selected()

@button_register(button=8, app="Google Sheets")
def sheets_merge_cells():
    # (see note below about the shortcut)
    macros.perform_hotkey(['alt', 'o']) # open Format
    time.sleep(0.05)
    macros.perform_press('m') # Merge cells submenu
    time.sleep(0.05)
    macros.perform_press('a') # Merge all (often 'A' / or Enter depending UI)


# @button_register(button=5)
# def tts_start():    
#     logger.debug("Text to Speech")
#     macros.textToSpeech()
    
# @button_register(button=6)
# def tts_stop():    
#     logger.debug("Stop Speech")
#     macros.stopSpeech()
    
# @button_register(button=7)
# def copy():    
#     logger.debug("Copy (Ctrl + C)")
#     macros.perform_hotkey(['ctrl', 'c'])
    
# @button_register(button=8)
# def past():    
#     logger.debug("Paste (Ctrl + V)")
#     macros.perform_hotkey(['ctrl', 'v'])
    
@button_register(button=9)
def search_highlighted_text():    
    logger.debug("Search highlighted text")
    macros.search_highlighted_text()
    
@button_register(button=10)
def task_manager():    
    logger.debug("Start Task manager")
    macros.start_task_viwer()
    
@button_register(button=11)
def screenshot_to_text():    
# case (11, _, _, []):
    logger.debug("Screenshot to text")
    macros.Image_to_text2()


# -- App Specific Controls --
# @button_register(button=5, app="Visual Studio Code")
# def vs_code_run():
#     logger.debug("VS Code: Run code (Ctrl + Alt + N)")
#     macros.perform_hotkey(['ctrl', 'alt', 'n'])

@button_register(button=5, app="Star Citizen")
def sc_focus_front_shields():
    logger.debug("Star Citizen: Focus front shields")
    macros.sheild_focus_star_citizen("1")

@button_register(button=6, app="Star Citizen")
def sc_focus_rear_shields():
    logger.debug("Star Citizen: Focus back shields")
    macros.sheild_focus_star_citizen("2")

@button_register(button=7, app="Star Citizen")
def sc_reses_shield_focus():
    logger.debug("Star Citizen: Reset shields")
    macros.sheild_focus_star_citizen("3")

# @button_register(button=7, app="factorio")
# def factorio_increase_area():
#     logger.debug('Factorio: Increase area')
#     macros.perform_press('add')

# @button_register(button=8, app="factorio")
# def factorio_decrease_area():
#     logger.debug('Factorio: Decrease area')
#     macros.perform_press('subtract')
    
    

# -- Soundboard Controls --
@button_register(button=5, layers=('Mode',))
def sb_plane_cut():
    logger.debug("Soundboard: Clanker - Plane")
    play_user_sound('plane-cut.mp3', 0.5)
    
@button_register(button=6, layers=('Mode',))
def sb_trump_come():
    logger.debug("Soundboard: Trump I'm gonna come")
    play_user_sound('trump-come.mp3', 0.5)
     
@button_register(button=7, layers=('Mode',))
def sb_wizard():
    logger.debug("Soundboard: Wizard")
    play_user_sound('wizard_cut.mp3', 0.5)
       
@button_register(button=8, layers=('Mode',))
def sb_bing_chilling():
    logger.debug("Soundboard: Bing Chilling")
    play_user_sound('bing-chilling.mp3', 0.5)
    
@button_register(button=9, layers=('Mode',))
def sb_hava():
    logger.debug("Soundboard: Hava")
    play_user_sound('hava3.mp3', 0.5)

@button_register(button=12, layers=('1', 'Mode'))
def sb_reset():
    logger.debug("Soundboard: Reset Soundboard Audio")
    # play_user_sound('hava3.mp3', 0.5)
    macros.soundboard.reset()


# -- Mode 2 Controls --
@button_register(button=5, mode=2)
def cut_text():
    logger.debug("Cut (Ctrl + X)")
    macros.perform_hotkey(['ctrl', 'x'])
    
@button_register(button=6, mode=2)
def audacity_split():
    logger.debug("Audacity Split (Ctrl + I)")
    macros.perform_hotkey(['ctrl', 'i'])
    
@button_register(button=9, mode=2)
def backspace():
    logger.debug("Backspace")
    macros.perform_press('backspace')    



# -------------------- Standard Encoder Controls --------------------

########################################    Encoder 1    ########################################
# @register_encoder(encoder_id=1, action='CCW')
# def volume_down():
#     macros.SpotifyController().event_handler('VolumeDown')

@register_encoder(encoder_id=1, action='CCWB')
def sp_backward_5s():
    logger.debug('Back5s')
    Spotify.event_handler('Back5s',)

@register_encoder(encoder_id=1, action='CWB')
def sp_forward_5s():
    logger.debug('Forward5s')
    Spotify.event_handler('Forward5s',)

########################################    Encoder 2    ########################################

@register_encoder(encoder_id=2, action='CCWB', app='LibreOffice Draw')
def draw_font_down():   
    logger.debug('Encoder2 rotate left, w/ button font_size_down')
    macros.libreOffice_font_size_down()

@register_encoder(encoder_id=2, action='CWB', app='LibreOffice Draw')
def draw_font_up():
    logger.debug('Encoder2 rotate right w/ button, font_size_up')
    macros.libreOffice_font_size_up()

@register_encoder(encoder_id=2, action='CCWB', app='LibreOffice Writer')
def writer_font_down():
    logger.debug('Encoder2 rotate left, w/ button font_size_down')
    macros.libreOffice_font_size_down()

@register_encoder(encoder_id=2, action='CWB', app='LibreOffice Writer')
def writer_font_up():
    logger.debug('Encoder2 rotate right w/ button, font_size_up')
    macros.libreOffice_font_size_up()
# zoomin in writer needs ctrl + scrollwheel


@register_encoder(encoder_id=2, action='CCW', app='factorio')
def factorio_increase_area():
    logger.debug('Encoder2 rotate left, Increase area')
    macros.perform_press('add')

@register_encoder(encoder_id=2, action='CW', app='factorio')
def factorio_decrease_area():
    logger.debug('Encoder2 rotate right, decrease area')
    macros.perform_press('subtract')



###TEMPORARY
@register_encoder(encoder_id=2, action='CCW', layers=('2',))
def zoom_in_2():
    logger.debug('Encoder2 rotate left, zoming out')
    macros.perform_press('left')

@register_encoder(encoder_id=2, action='CW', layers=('2',))
def zoom_out_2():
    logger.debug('Encoder2 rotate right, zoming in')
    macros.perform_press('right')   


@register_encoder(encoder_id=2, action='CW', layers=('Mode',))
def zoom_reset():
    logger.debug('Encoder2 rotate right with mode, reseting zoom')
    macros.perform_hotkey(['ctrl', '0'])  

@register_encoder(encoder_id=2, action='CCWB')
def left_arrow():
    logger.debug('Encoder2 rotate left w/ button, left arrow')
    macros.perform_press('left')

@register_encoder(encoder_id=2, action='CWB')
def right_arrow():
    logger.debug('Encoder2 rotate right w/ button, right arrow')
    macros.perform_press('right')  