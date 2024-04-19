import logging
import datetime
import os

# for notiffications
from win10toast import ToastNotifier
toaster = ToastNotifier()


#Script directory
script_path = os.path.dirname(os.path.abspath(__file__))
log_folder_path = r'C:\Users\Taylor\Desktop\Macro Logs'

def log_folder(log_folder_path):
    """Returns path to log folder with version name.\n
    Will create a folder at that path location.
    
    Define log_folder_path as the path of the log folder you want.
    """
    version = __file__.split('\\')[-2]
    version = version.upper()
        
    log_folder = f'{log_folder_path}\{version}'

    if os.path.isdir(log_folder):
        return log_folder
    os.mkdir(log_folder)

    return log_folder

class CustomFormatter(logging.Formatter):
    MAGENTA = "\u001b[35m"
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = '%(asctime)s.%(msecs)03d %(levelname)s - %(funcName)s: %(message)s'

    FORMATS = {
        logging.DEBUG: MAGENTA + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt='%H:%M:%S')
        return formatter.format(record)


# Creates a file path for the log file.
now = datetime.datetime.now()
path = log_folder(log_folder_path)
log_file_name = now.strftime("%Y-%B-%d_%H.%M.%S")
filename = f'{path}\{log_file_name}.log'

# # create logger
logger = logging.getLogger("My_app")
logger.setLevel(logging.DEBUG)

log_file_format = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s - %(funcName)s: %(message)s', datefmt='%H:%M:%S') 

file_handler = logging.FileHandler(filename)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(log_file_format)

stream_handler = logging.StreamHandler()

stream_handler.setFormatter(CustomFormatter())
logger.addHandler(file_handler)
logger.addHandler(stream_handler)