# import time
from device import MacroDriver
from logger_setup import setup_logging, get_logger
# from config import load_settings
from config import load_settings, settings
from system_tray import create_tray_icon, stop_tray_icon
# from system_tray import create_tray_icon, stop_tray_icon, show_notification
# from notifications import send_notification # Import the new function

# --- Startup procedure ---
load_settings()
# settings._list()
setup_logging()
logger = get_logger('DriverMain')
is_running = True

def quit_application():
    """Function to be called when the application should shut down."""
    global is_running
    is_running = False
    macro_driver.stop()


def main():
    """The main application entry point and control loop."""
    logger.info("Initializing device driver.")

    pause_enabled = settings.get('features.keyboard_pause_btn', False)
    logger.info(f"Keyboard pause button feature enabled: {pause_enabled}")
    # --- Create the MacroDriver instance ---
    global macro_driver
    macro_driver = MacroDriver(enable_pause_btn=pause_enabled)

    # --- Start System Tray Icon ---
    create_tray_icon(quit_application)

    # ... (other initialization)
    
    try:
        # --- Main read loop ---
        logger.info("Starting main loop. Use the tray icon to exit.")
        macro_driver.read_loop() # The loop will handle its own connection management
    except Exception as e:
        logger.critical(f"Unhandled exception in main loop: {e}", exc_info=True)
    finally:
        # --- Cleanup ---
        stop_tray_icon()
        macro_driver.stop()
        logger.info("Application finished.")

if __name__ == "__main__":
    main()