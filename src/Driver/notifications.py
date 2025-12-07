import sys
import os
# import logging
# from threading import Thread

from config import settings
from logger_setup import get_logger
logger = get_logger("Notifications")

if sys.platform == 'win32':
    try:
        from win10toast import ToastNotifier
        toaster = ToastNotifier()
    except ImportError:
        logger.warning("win10toast not installed. Install with 'pip install win10toast' for Windows notifications.")
        ToastNotifier = None
else:
    # ToastNotifier = None
    toaster = None

# toaster = ToastNotifier() if platform.system().lower() == 'windows' and ToastNotifier else None

def _send_notification_linux(msg, urgency, expire_time, app_name):
    """Internal function for sending notifications on Linux."""
    try:
        cmd = f'notify-send -u {urgency} -t {expire_time*1000} -a {app_name} "{msg}"'
        os.system(cmd)
    except Exception as e:
        logger.warning(f"Failed to send Linux notification: {e}")

def _send_notification_windows(title, msg, expire_time, threaded):
    """Internal function for sending notifications on Windows."""
    if toaster:
        try:
            toaster.show_toast(title, msg, duration=expire_time, threaded=threaded)
        except Exception as e:
            logger.warning(f"Failed to send Windows notification: {e}")
    else:
        logger.warning("Windows notification requested, but 'win10toast' is not available.")

def send_notification(**kwargs):
    """
    Wrapper function to send platform-specific notifications.
    
    :param msg:            Your message.
    :param urgency:        low, normal, critical (Linux only).
    :param expire_time:    Specifies the timeout in seconds.
    :param app_name:       Specifies the app name for the icon (Linux only).
    :param threaded:       True or False (Windows only), True by default.
    :param title:          str, the title of the notification (Windows only).
    """
    if sys.platform == 'win32' and not toaster:
        logger.warning("Notification system not set up for Windows. Check dependencies.")
        return

    # Use getattr to safely retrieve settings, or rely on kwargs
    expire_time = settings.get('app.notification_time', 2)
    
    # Keyword arguments override default values
    msg = kwargs.get('msg')
    urgency = kwargs.get('urgency', 'normal')
    expire_time = kwargs.get('expire_time', expire_time)
    app_name = kwargs.get('app_name', settings.get('app.app_name', 'DefaultApp'))
    threaded = kwargs.get('threaded', True)
    title = kwargs.get('title', "Warning")

    if not msg:
        logger.warning("Notification message is required.")
        return

    plat = sys.platform
    try:
        if plat.startswith('linux'):
            _send_notification_linux(msg, urgency, expire_time, app_name)
        elif plat == 'win32':
            _send_notification_windows(title, msg, expire_time, threaded)
        else:
            logger.warning(f"Unsupported platform for notifications: {plat}")
    except Exception as e:
        logger.warning(f"Error in send_notification function: {e}")

