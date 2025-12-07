import logging
import datetime
from config import settings

def addLoggingLevel(levelName, levelNum, methodName=None):
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class. (Adapted from old logger code)
    """
    if not methodName:
        methodName = levelName.lower()

    if hasattr(logging, levelName):
       raise AttributeError('{} already defined in logging module'.format(levelName))
    if hasattr(logging, methodName):
       raise AttributeError('{} already defined in logging module'.format(methodName))
    if hasattr(logging.getLoggerClass(), methodName):
       raise AttributeError('{} already defined in logger class'.format(methodName))
       
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)
    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)

# Add the custom TRACE level to the logging module
addLoggingLevel('TRACE', 5)

class CustomFormatter(logging.Formatter):
    """Uses ANSI escape codes for console output. (Adapted from old logger code)"""
    MAGENTA = "\u001b[35m"
    BLUE = "\x1b[34;20m"
    GREY = "\x1b[38;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"
    # Note: %(filename)s is no longer included in the format to prevent
    # the color escape code from being written to the file handler.
    # format_base = '%(asctime)s.%(msecs)03d %(levelname)s - %(funcName)s: %(message)s'
    # format_base = '%(asctime)s.%(msecs)03d - %(filename)s/%(funcName)s - %(levelname)s: %(message)s'
    format_base = '%(asctime)s.%(msecs)03d - %(levelname)s - %(filename)s/%(funcName)s: %(message)s'

    FORMATS = {
        logging.INFO: GREY + format_base + RESET,
        logging.DEBUG: MAGENTA + format_base + RESET,
        # logging.getLevelName('TRACE'): BLUE + format_base + RESET,
        logging.TRACE: BLUE + format_base + RESET,  # Corrected line
        logging.WARNING: YELLOW + format_base + RESET,
        logging.ERROR: RED + format_base + RESET,
        logging.CRITICAL: BOLD_RED + format_base + RESET
    }
    
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt='%H:%M:%S')
        return formatter.format(record)

# --- New modular setup function ---

def setup_logging():
    """Configures the logging for the application using settings from config.yml."""
    log_enabled = settings.get('logging.enabled', False)
    if not log_enabled:
        logging.basicConfig(level=logging.CRITICAL)
        return
    
    # Clear any existing handlers to prevent duplicate logs
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    log_level_str = settings.get('logging.level', 'INFO')
    log_level_int = getattr(logging, log_level_str.upper(), logging.INFO)
    # log_level_int = logging.getLevelName(log_level_str.upper())
    
    # Create the root logger and set its level
    root_logger.setLevel(log_level_int)

    # Console Handler
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level_int)
    stream_handler.setFormatter(CustomFormatter())
    root_logger.addHandler(stream_handler)
    
    # Define a different format for the file handler to avoid ANSI color codes
    file_format = logging.Formatter(
        '%(asctime)s.%(msecs)03d - %(levelname)s - %(filename)s/%(funcName)s: %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # File Handler
    if settings.get('logging.folder.enabled', False):
        project_root = settings._config_dir
        if not project_root:
            # Fallback if config_dir is not set
            logging.error("Configuration directory not set. Cannot configure file logging.")
            return

        log_folder_path = settings.get('logging.folder.path')
        if not log_folder_path:
            log_folder_path = project_root / settings.get('logging.folder.relative_path', 'logs')
        
        log_folder_path.mkdir(parents=True, exist_ok=True)
        
        # Create a unique filename with a timestamp
        now = datetime.datetime.now()
        log_file_name = now.strftime("%Y-%m-%d_%H.%M.%S.log")
        log_file_path = log_folder_path / log_file_name
        
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(log_level_int)
        file_handler.setFormatter(file_format)
        root_logger.addHandler(file_handler)

def get_logger(name):
    """Returns a logger for a specific module."""
    return logging.getLogger(name)

