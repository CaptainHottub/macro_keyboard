"""
my_device_driver/           # folder
├── src/
│    ├── Case/
│    ├── Microcontroller/
│    ├── PCB/
│    └── Driver/
│           ├── _linux_macros.py
│           ├── _soundboard.py
│           ├── _windows_macros.py
│           ├── config.py
│           ├── logger_setup.py
│           ├── device.py
│           ├── driver_main.py
│           ├── macros.py
│           └── ...
│
├── config.yml              # The configuration file
├── README.md
└── requirements.txt
"""
# src/Driver/config.py
import yaml
import os
import logging
from pathlib import Path

class AppConfig:
    """Class to hold and provide access to application settings."""
    def __init__(self):
        self._config = {}
        self._config_dir = None  # Add an attribute to store the directory

    
    def _list(self):
        """Prints all the loaded configs"""
        for key, value in self._config.items():
            print(f"Key: {key}, Value: {value}")
            
    def load(self, config_path):
        """Loads configuration from a YAML file."""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found at {config_path}")
            
        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)
        
        # Store the directory of the loaded configuration file
        self._config_dir = Path(config_path).parent

    def get(self, key, default=None):
        """Safely retrieves a configuration value by a dot-separated key."""
        keys = key.split('.')
        value = self._config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

settings = AppConfig()


# Add the custom level name to the logging module's name-to-level mapping
# This is required for `logging.getLevelName` to work with the string 'TRACE'
if "TRACE" not in logging._nameToLevel:
    logging.addLevelName(5, "TRACE")


def load_settings(config_file="config.yml"):
    """
    Loads application settings from a YAML file by traversing up the
    directory tree from the current file's location.
    """
    # Get the directory of the currently executing script
    current_dir = Path(__file__).resolve().parent
    # Traverse up the directory tree to find the config.yml file
    config_path = None
    for parent in current_dir.parents:
        potential_path = parent / config_file
        if potential_path.is_file():
            config_path = potential_path
            break
    
    if not config_path:
        logging.error(f"FATAL: Could not find '{config_file}' by searching parent directories.")
        raise SystemExit(1)
    
    try:
        settings.load(config_path)
    except FileNotFoundError as e:
        # This is unlikely to be reached due to the check above, but included for robustness
        logging.error(f"FATAL: {e}")
        raise SystemExit(1)
    except yaml.YAMLError as e:
        logging.error(f"FATAL: Error parsing YAML file: {e}")
        raise SystemExit(1)
