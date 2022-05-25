import ctypes
from ctypes import wintypes
import time

user32 = ctypes.WinDLL('user32', use_last_error=True)

INPUT_MOUSE    = 0
INPUT_KEYBOARD = 1

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP       = 0x0002
KEYEVENTF_UNICODE     = 0x0004
KEYEVENTF_SCANCODE    = 0x0008

MAPVK_VK_TO_VSC = 0

# msdn.microsoft.com/en-us/library/dd375731
VK_TAB  = 0x09
VK_MENU = 0x12



class isNotValid(Exception):
    """Exception raise when key is not valid """
    def __init__(self, key, message="Key is not in list of valid keys"):
        self.key = key
        self.message = message
        super().__init__(self.message)
    def __str__(self):
        return f'{self.key} -> {self.message}'

# C struct definitions

wintypes.ULONG_PTR = wintypes.WPARAM

class MOUSEINPUT(ctypes.Structure):
    _fields_ = (("dx",          wintypes.LONG),
                ("dy",          wintypes.LONG),
                ("mouseData",   wintypes.DWORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk",         wintypes.WORD),
                ("wScan",       wintypes.WORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

    def __init__(self, *args, **kwds):
        super(KEYBDINPUT, self).__init__(*args, **kwds)
        # some programs use the scan code even if KEYEVENTF_SCANCODE
        # isn't set in dwFflags, so attempt to map the correct code.
        if not self.dwFlags & KEYEVENTF_UNICODE:
            self.wScan = user32.MapVirtualKeyExW(self.wVk,
                                                 MAPVK_VK_TO_VSC, 0)

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),
                    ("mi", MOUSEINPUT))#,
                    #("hi", HARDWAREINPUT))
    _anonymous_ = ("_input",)
    _fields_ = (("type",   wintypes.DWORD),
                ("_input", _INPUT))

LPINPUT = ctypes.POINTER(INPUT)

def _check_count(result, func, args):
    if result == 0:
        raise ctypes.WinError(ctypes.get_last_error())
    return args

user32.SendInput.errcheck = _check_count
user32.SendInput.argtypes = (wintypes.UINT, # nInputs
                             LPINPUT,       # pInputs
                             ctypes.c_int)  # cbSize

# # from pyautogui
# Keyboard_Codes = {
#     'backspace': 0x08, # VK_BACK
#     '\b': 0x08, # VK_BACK
#     'super': 0x5B, #VK_LWIN
#     'tab': 0x09, # VK_TAB
#     '\t': 0x09, # VK_TAB
#     'clear': 0x0c, # VK_CLEAR
#     'enter': 0x0d, # VK_RETURN
#     '\n': 0x0d, # VK_RETURN
#     'return': 0x0d, # VK_RETURN
#     'shift': 0x10, # VK_SHIFT
#     'ctrl': 0x11, # VK_CONTROL
#     'alt': 0x12, # VK_MENU
#     'pause': 0x13, # VK_PAUSE
#     'capslock': 0x14, # VK_CAPITAL
#     'kana': 0x15, # VK_KANA
#     'hanguel': 0x15, # VK_HANGUEL
#     'hangul': 0x15, # VK_HANGUL
#     'junja': 0x17, # VK_JUNJA
#     'final': 0x18, # VK_FINAL
#     'hanja': 0x19, # VK_HANJA
#     'kanji': 0x19, # VK_KANJI
#     'esc': 0x1b, # VK_ESCAPE
#     'escape': 0x1b, # VK_ESCAPE
#     'convert': 0x1c, # VK_CONVERT
#     'nonconvert': 0x1d, # VK_NONCONVERT
#     'accept': 0x1e, # VK_ACCEPT
#     'modechange': 0x1f, # VK_MODECHANGE
#     ' ': 0x20, # VK_SPACE
#     'space': 0x20, # VK_SPACE
#     'pgup': 0x21, # VK_PRIOR
#     'pgdn': 0x22, # VK_NEXT
#     'pageup': 0x21, # VK_PRIOR
#     'pagedown': 0x22, # VK_NEXT
#     'end': 0x23, # VK_END
#     'home': 0x24, # VK_HOME
#     'left': 0x25, # VK_LEFT
#     'up': 0x26, # VK_UP
#     'right': 0x27, # VK_RIGHT
#     'down': 0x28, # VK_DOWN
#     'select': 0x29, # VK_SELECT
#     'print': 0x2a, # VK_PRINT
#     'execute': 0x2b, # VK_EXECUTE
#     'prtsc': 0x2c, # VK_SNAPSHOT
#     'prtscr': 0x2c, # VK_SNAPSHOT
#     'prntscrn': 0x2c, # VK_SNAPSHOT
#     'printscreen': 0x2c, # VK_SNAPSHOT
#     'insert': 0x2d, # VK_INSERT
#     'del': 0x2e, # VK_DELETE
#     'delete': 0x2e, # VK_DELETE
#     'help': 0x2f, # VK_HELP
#     'win': 0x5b, # VK_LWIN
#     'winleft': 0x5b, # VK_LWIN
#     'winright': 0x5c, # VK_RWIN
#     'apps': 0x5d, # VK_APPS
#     'sleep': 0x5f, # VK_SLEEP
#     'num0': 0x60, # VK_NUMPAD0
#     'num1': 0x61, # VK_NUMPAD1
#     'num2': 0x62, # VK_NUMPAD2
#     'num3': 0x63, # VK_NUMPAD3
#     'num4': 0x64, # VK_NUMPAD4
#     'num5': 0x65, # VK_NUMPAD5
#     'num6': 0x66, # VK_NUMPAD6
#     'num7': 0x67, # VK_NUMPAD7
#     'num8': 0x68, # VK_NUMPAD8
#     'num9': 0x69, # VK_NUMPAD9
#     'multiply': 0x6a, # VK_MULTIPLY  ??? Is this the numpad *?
#     'add': 0x6b, # VK_ADD  ??? Is this the numpad +?
#     'separator': 0x6c, # VK_SEPARATOR  ??? Is this the numpad enter?
#     'subtract': 0x6d, # VK_SUBTRACT  ??? Is this the numpad -?
#     'decimal': 0x6e, # VK_DECIMAL
#     'divide': 0x6f, # VK_DIVIDE
#     'f1': 0x70, # VK_F1
#     'f2': 0x71, # VK_F2
#     'f3': 0x72, # VK_F3
#     'f4': 0x73, # VK_F4
#     'f5': 0x74, # VK_F5
#     'f6': 0x75, # VK_F6
#     'f7': 0x76, # VK_F7
#     'f8': 0x77, # VK_F8
#     'f9': 0x78, # VK_F9
#     'f10': 0x79, # VK_F10
#     'f11': 0x7a, # VK_F11
#     'f12': 0x7b, # VK_F12
#     'f13': 0x7c, # VK_F13
#     'f14': 0x7d, # VK_F14
#     'f15': 0x7e, # VK_F15
#     'f16': 0x7f, # VK_F16
#     'f17': 0x80, # VK_F17
#     'f18': 0x81, # VK_F18
#     'f19': 0x82, # VK_F19
#     'f20': 0x83, # VK_F20
#     'f21': 0x84, # VK_F21
#     'f22': 0x85, # VK_F22
#     'f23': 0x86, # VK_F23
#     'f24': 0x87, # VK_F24
#     'numlock': 0x90, # VK_NUMLOCK
#     'scrolllock': 0x91, # VK_SCROLL
#     'shiftleft': 0xa0, # VK_LSHIFT
#     'shiftright': 0xa1, # VK_RSHIFT
#     'ctrlleft': 0xa2, # VK_LCONTROL
#     'ctrlright': 0xa3, # VK_RCONTROL
#     'altleft': 0xa4, # VK_LMENU
#     'altright': 0xa5, # VK_RMENU
#     'browserback': 0xa6, # VK_BROWSER_BACK
#     'browserforward': 0xa7, # VK_BROWSER_FORWARD
#     'browserrefresh': 0xa8, # VK_BROWSER_REFRESH
#     'browserstop': 0xa9, # VK_BROWSER_STOP
#     'browsersearch': 0xaa, # VK_BROWSER_SEARCH
#     'browserfavorites': 0xab, # VK_BROWSER_FAVORITES
#     'browserhome': 0xac, # VK_BROWSER_HOME
#     'volumemute': 0xad, # VK_VOLUME_MUTE
#     'volumedown': 0xae, # VK_VOLUME_DOWN
#     'volumeup': 0xaf, # VK_VOLUME_UP
#     'nexttrack': 0xb0, # VK_MEDIA_NEXT_TRACK
#     'prevtrack': 0xb1, # VK_MEDIA_PREV_TRACK
#     'stop': 0xb2, # VK_MEDIA_STOP
#     'playpause': 0xb3, # VK_MEDIA_PLAY_PAUSE
#     'launchmail': 0xb4, # VK_LAUNCH_MAIL
#     'launchmediaselect': 0xb5, # VK_LAUNCH_MEDIA_SELECT
#     'launchapp1': 0xb6, # VK_LAUNCH_APP1
#     'launchapp2': 0xb7, # VK_LAUNCH_APP2
#     }


# # Category variables
# letters = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
# shiftsymbols = "~!@#$%^&*()_+QWERTYUIOP{}|ASDFGHJKL:\"ZXCVBNM<>?"

# def isvalid(key):

#     if key not in Keyboard_Codes:
#         raise isNotValid(key)
#     return Keyboard_Codes[key]
   
# I can try and copy Pyautogui, a bit. it doesnt use user32.SendInput, so numpad keys arent registered correctly
# Functions
def PressKey(key):
    x = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=key))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))
    
def ReleaseKey(KeyCode):
    x = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=KeyCode, dwFlags=KEYEVENTF_KEYUP))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))


# def SendKey(KeyCode):
#     # if KeyCode in Keyboard_Codes:
#     #     VK_code = hex(Keyboard_Codes[KeyCode])

#     VK_code = isvalid(KeyCode)

#     x1 = INPUT(type=INPUT_KEYBOARD,
#               ki=KEYBDINPUT(wVk=VK_code))
#     x2 = INPUT(type=INPUT_KEYBOARD,
#               ki=KEYBDINPUT(wVk=VK_code, dwFlags=KEYEVENTF_KEYUP))
   
#     user32.SendInput(1, ctypes.byref(x1), ctypes.sizeof(x1))
#     time.sleep(0.2)
#     user32.SendInput(1, ctypes.byref(x2), ctypes.sizeof(x2))




# def HotKey(*keys):
#     # gets the key_code of the keys we want pressed
#     VK_codes = isvalid(keys)
    
#     print(VK_codes)
#     #VK_codes = [hex(Keyboard_Codes[key]) for key in hexKeyCodes  if key in Keyboard_Codes]


# # sorta works needs to hold down key,
# def keyTest(*keys):


#     print(keys)
#     #log.debug("entering for loop")
#     for c in keys:
#         #log.debug(c)
#         if len(c) > 1:
#             c = c.lower()
#         PressKey(c)

#     for c in reversed(keys):
#         if len(c) > 1:
#             c = c.lower()
#         ReleaseKey(c)
#         #time.sleep(interval)

#     # for c in args:
#     #     if len(c) > 1:
#     #         c = c.lower()
#     #     platformModule._keyDown(c)
#     #     time.sleep(interval)
#     # for c in reversed(args):
#     #     if len(c) > 1:
#     #         c = c.lower()
#     #     platformModule._keyUp(c)
#     #     time.sleep(interval)