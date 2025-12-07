import pystray
from PIL import Image
from pathlib import Path
from threading import Thread

from config import settings
# from config import settings, load_settings
from logger_setup import get_logger

logger = get_logger("SystemTray")
icon_thread = None
tray_icon = None

def get_project_root():
    """Helper function to find the project root for accessing assets."""
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir
    while project_root.name != "my_device_driver" and project_root.parent != project_root:
        project_root = project_root.parent
    return project_root

def create_tray_icon(main_loop_callback):
    """
    Creates and starts the system tray icon in a new thread.
    The main_loop_callback is a function to execute when "Quit" is selected.
    """
    global icon_thread, tray_icon

    if not settings.get('system_tray.enabled'):
        return

    icon_relative_path = settings.get('system_tray.icon.relative_path')
    if not icon_relative_path:
        logger.warning("Relative icon path not specified in config. Not showing tray icon.")
        return
    
    project_root = settings._config_dir
    # project_root = get_project_root()
    icon_path = project_root / icon_relative_path
    
    try:
        image = Image.open(icon_path)
    except FileNotFoundError:
        logger.error(f"Icon file not found at: {icon_path}")
        return

    def on_quit(icon, item):
        logger.info("Quitting via tray icon...")
        icon.stop()
        main_loop_callback()

    menu = (
        pystray.MenuItem('Quit', on_quit),
    )

    tray_icon = pystray.Icon('macro_keyboard_driver', image, 'Macro Keyboard Driver', menu)
    
    def run_icon():
        tray_icon.run()

    icon_thread = Thread(target=run_icon, daemon=True)
    icon_thread.start()
    
    logger.info("System tray icon started.")

def stop_tray_icon():
    """Stops the system tray icon."""
    global tray_icon
    if tray_icon:
        tray_icon.stop()
        tray_icon = None
        logger.info("System tray icon stopped.")

def show_notification(title, message):
    """Displays a system tray notification."""
    global tray_icon
    if tray_icon:
        tray_icon.notify(message, title)
