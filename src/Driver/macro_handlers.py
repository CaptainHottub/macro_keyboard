import threading
import inspect
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from config import settings
from logger_setup import get_logger
import macros  # Your main library of tools

Spotify = macros.SpotifyController()
logger = get_logger("MacroHandlers")



# ---  Thread Safety (The "Mash" Protection) ---
# We create a pool of workers to handle button presses. 
# This prevents the driver from crashing if you spam buttons.
EXECUTOR = ThreadPoolExecutor(max_workers=8)

# ---  Setup Safe Paths ---
SOUND_DIR = Path(settings.get('paths.sounds', '~/Documents/soundboard_audios')).expanduser()


# --- BUTTON REGISTRY ---
MACRO_REGISTRY = {}
def button_register(button, app=None, mode=None, layers=()):
    """
    A decorator that registers a function to a specific button combination.
    
    Arguments:
        button (int): The button ID.
        app (str): Specific app name (or None for any app).
        mode (int): Specific mode number (or None for any mode).
        layers (tuple): A tuple of layer names (e.g., ('Mode',)).
    """
    def decorator(func):
        # We sort the layers to ensure ('Mode', 'Shift') is the same as ('Shift', 'Mode')
        key = (app, mode, button, tuple(sorted(layers)))
        MACRO_REGISTRY[key] = func
        return func
    return decorator
    
    
# --- ENCODER REGISTRY ---
ENCODER_REGISTRY = {}
def register_encoder(encoder_id, action, app=None, mode=None, layers=()):
    """
    Registers a function to an encoder action.
    
    Arguments:
        encoder_id (int): 1 or 2
        action (str): 'RL' (Rotate Left), 'RR' (Rotate Right), 
                      'RLB' (Left while pressed), 'RRB' (Right while pressed)
    """
    def decorator(func):
        # Key: (App, Mode, EncoderID, Action, Layers)
        key = (app, mode, encoder_id, action, tuple(sorted(layers)))
        ENCODER_REGISTRY[key] = func
        return func
    return decorator    
    
    


# --- Helper Functions ---
def play_user_sound(filename, volume):
    """
    Plays a sound from the soundboard directory. 
    Users just pass 'plane.mp3', we handle the paths and threading.
    """
    # We use the internal SOUND_DIR we already defined
    full_path = str(SOUND_DIR / filename)
    # We submit to the executor so it doesn't block their macro
    EXECUTOR.submit(macros.soundboard.play_on_multiple_devices, full_path, volume)


# ---  Import User Macros ---
try:
    import user_macros
    logger.info("Successfully loaded user_macros.py")
except ImportError:
    logger.info("No user_macros.py found. Using default macros only.")
except Exception as e:
    logger.error(f"Error loading user_macros.py: {e}")



# --- BUTTON HANDLER ---

def button_handler(event_data, mode, app_data, macro_driver):
    button_id = event_data['Button_id']
    layers = tuple(sorted(event_data.get('Layers', [])))
    app_name = app_data['app']
    focused_window_hwnd = app_data['hwnd']
    logger.debug(f"Handling Button: ID={button_id}, App={app_name}, Mode={mode}, Layers={layers}")
        
    # Generate Priority List
    candidate_keys = [
        (app_name, mode, button_id, layers),
        (app_name, None, button_id, layers),
        (None, mode, button_id, layers),
        (None, None, button_id, layers)
    ]

    for key in candidate_keys:
        if key in MACRO_REGISTRY:
            action = MACRO_REGISTRY[key]
            
           
            # --- SMART EXECUTION ---
            # We look at what arguments the function is asking for.
            sig = inspect.signature(action)
            params = sig.parameters
            
            # Prepare the arguments we CAN provide
            # You can add more context variables here if you want!
            possible_args = {
                'mode': mode,
                'app': app_name,
                'button': button_id,
                'hwnd': focused_window_hwnd
            }
            
            # Filter: Only pass the arguments the function actually requested
            kwargs = {k: v for k, v in possible_args.items() if k in params}
            
            # Submit to the thread pool with the correct arguments
            try:
                EXECUTOR.submit(action, **kwargs)
            except Exception as e:
                logger.error(f"Error submitting macro: {e}")
            
            return

    logger.info(f"No macro found for Button {button_id}")




"""Button Layout
     +----+----+----+----+
     |  1 |  2 |  3 |  4 |
     +----+----+----+----+
     |  5 |  6 |  7 |  8 |
+----+----+----+----+----+
|mode|  9 | 10 | 11 | 12 |
+----+----+----+----+----+
"""
# --- DEFAULT BUTTON MACROS ---
@button_register(button=1)
def show_mode(mode):
    macros.ButtonMode(mode)

# -- Global Media Controls --
@button_register(button=2)
def spotify_play_pause():
    Spotify.press()

@button_register(button=5)
def text_to_speech():
    macros.textToSpeech()

@button_register(button=6)
def stop_speech():
    macros.stopSpeech()




# --- ENCODER HANDLER ---

def encoder_handler(event_data, mode, app_data):
    encoder_id = event_data['Encoder'][0]['Id']
    action_type = event_data['Encoder'][0]['Value'] # 'RL', 'RR', etc.
    layers = tuple(sorted(event_data.get('Layers', [])))
    app_name = app_data['app']

    logger.debug(f"Handling Encoder: ID={encoder_id}, Action={action_type}, App={app_name}")

    # Priority List:
    # 1. Exact Match (App + Mode)
    # 2. App Specific (Any Mode)
    # 3. Mode Specific (Any App)
    # 4. Global (Any App, Any Mode)
    candidate_keys = [
        (app_name, mode, encoder_id, action_type, layers),
        (app_name, None, encoder_id, action_type, layers),
        (None, mode, encoder_id, action_type, layers),
        (None, None, encoder_id, action_type, layers)
    ]

    for key in candidate_keys:
        if key in ENCODER_REGISTRY:
            func = ENCODER_REGISTRY[key]
            
            # Inspect the function
            sig = inspect.signature(func)
            params = sig.parameters

            # Prepare args (Encoders might want different data)
            possible_args = {
                'mode': mode,
                'app': app_name,
                'encoder_id': encoder_id,
                'action': action_type
            }
            
            kwargs = {k: v for k, v in possible_args.items() if k in params}
            
            EXECUTOR.submit(func, **kwargs)
            return
        
    logger.info(f"No macro found for Encoder {encoder_id} action {action_type}")
    
    
# --- DEFAULT ENCODER MACROS ---

# Global Volume Control (Encoder 1)
@register_encoder(encoder_id=1, action='RL')
def volume_down():
    macros.SpotifyController().event_handler('VolumeDown')

@register_encoder(encoder_id=1, action='RR')
def volume_up():
    macros.SpotifyController().event_handler('VolumeUp')

# Zooming (Encoder 2 - Default)
@register_encoder(encoder_id=2, action='RL')
def zoom_out():
    macros.perform_hotkey(['ctrl', '-'])

@register_encoder(encoder_id=2, action='RR')
def zoom_in():
    macros.perform_hotkey(['ctrl', '='])
    """
    I did 'ctrl' + '=', because the + symbol requires the Shift key
    so what happens is 'ctrl' + 'shift' + '=' to get 'ctrl' + '+'
    and in adobe acrobat pdf extension, 'ctrl' + 'shift' + '=' rotates the page.
    """
    
    
# App Specific: LibreOffice (Encoder 2)
@register_encoder(encoder_id=2, action='RL', app='LibreOffice Draw')
def draw_zoom_out():
    macros.libreOffice_zoomout()

@register_encoder(encoder_id=2, action='RR', app='LibreOffice Draw')
def draw_zoom_in():
    macros.libreOffice_zoomin()