import contextlib
import logging
import threading
import time
import warnings
import psutil
from pywinauto import Application

import pyautogui

### find PID of app, 
def findProcessIdByName(processName):
  """
  Returns a list of all the process ID's with a specific name.
  
  Args:
    processName (str) - Name of the process you want to find.
      Ex: "Spotify"
    
  Returns:
    (listOfProcessIds) List of all process ID's with a specific name.

  NOTE: Function will not work if processName is empty
  """
  listOfProcessIds = []
  for proc in psutil.process_iter():
      with contextlib.suppress(psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
          pinfo = proc.as_dict(attrs=['pid', 'name'])
          if processName.lower() in pinfo['name'].lower() :
              listOfProcessIds.append(pinfo['pid'])
  return listOfProcessIds





