# -*- coding: utf-8 -*-
import logging
import datetime
import os
import sys
import yaml


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

def send_notification(**kwargs):
    """
    its a wrapper of sort. it creates notifications one way on linux and another way on windows

    :param msg:            Your message
    :param urgency:        low, normal, critical
    :param expire_time:    Specifies the timeout in milliseconds at which to expire the notification. 2 by default, defined in config
    :param app_name:       Specifies the app name for the icon, default is name of script
    :param threaded:       True of False    True by default
    :param title:          str, its the title of the notification and only for windows, Warning by default
    """

    urgency = 'low'
    expire_time = config['notification_time']
    app_name = os.path.basename(__file__)
    threaded = True
    title= "Warning"

    if 'urgency' in kwargs and kwargs['urgency'] is not None:
        urgency = kwargs['urgency']
    if 'expire_time' in kwargs and kwargs['expire_time'] is not None:
        expire_time = kwargs['expire_time']    
    if 'app_name' in kwargs and kwargs['app_name'] is not None:
        app_name = kwargs['app_name']
    if 'threaded' in kwargs and kwargs['threaded'] is not None:
        threaded = kwargs['threaded']
    if 'title' in kwargs and kwargs['title'] is not None:
        title = kwargs['title']

    try:
        if plat == 'linux':
            if 'msg' in kwargs:
                cmd = f'notify-send -u {urgency} -t {expire_time*1000} -a {app_name} "{kwargs['msg']}"'
                os.system(cmd)

        elif plat == 'win32':
            if 'msg' in kwargs:
                #toaster.show_toast("Warning", "Some features may not work on Linux", duration=2, threaded=True)
                toaster.show_toast(title, kwargs['msg'], duration=(expire_time), threaded=threaded)
    
    except Exception as e:
        logger.warning(e)
        
def get_version(file_dir)-> str:
    """Looks through the CHANGELOG.md file for the version number

    Returns:
        str: The version number
    """
    changelog_path = file_dir+'/CHANGELOG.md'
    
    try:
        string_with_version_in_it = ''
        with open(changelog_path,'r') as file:
            for line in file:
                if '##' in line:
                    string_with_version_in_it = line
                    file.close()
                    break    
                
        version = string_with_version_in_it[4:12]
    except FileNotFoundError:
        print('CHANGELOG.md Not Found, version will be ""')
        version = ''

    return version

plat = sys.platform.lower()

if sys.platform == 'win32':
    from win10toast import ToastNotifier
    toaster = ToastNotifier()
    #toaster.show_toast("Warning", "Some features may not work on Linux", duration=2, threaded=True)
   
script_path = os.path.dirname(__file__)
file_directory_temp = script_path.split('/')[0:-2]
file_dir = '/'.join(file_directory_temp)
#print(file_dir)

config = yaml.safe_load(open(f'{file_dir}/config.yml'))
print(config)

version = get_version(file_dir)

if config['logging']:
    logger = logging.getLogger("My_app")
    stream_handler = logging.StreamHandler()
    if config['logging_level'] == 'INFO':
        logger.setLevel(logging.INFO)
        stream_handler.setLevel(logging.INFO)

    elif config['logging_level'] == 'DEBUG':
        logger.setLevel(logging.DEBUG)
        stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(CustomFormatter())
    logger.addHandler(stream_handler)


    if config['log_folder']:
        now = datetime.datetime.now()
        log_file_name = now.strftime("%Y-%B-%d_%H.%M.%S")
        if config['log_folder_path'] != '' and config['log_folder_path_relative'] == '':
            filename = f'{config['log_folder_path']}/{log_file_name}.log'
            
        elif config['log_folder_path_relative'] != '' and config['log_folder_path'] == '':
            filename = f'{file_dir}/{config['log_folder_path_relative']}/{log_file_name}.log'

        file_handler = logging.FileHandler(filename)

        if config['logging_level'] == 'INFO':
            file_handler.setLevel(logging.INFO)
        elif config['logging_level'] == 'DEBUG':
            file_handler.setLevel(logging.DEBUG)

        log_file_format = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s - %(funcName)s: %(message)s', datefmt='%H:%M:%S') 

        file_handler.setFormatter(log_file_format)
        logger.addHandler(file_handler)

