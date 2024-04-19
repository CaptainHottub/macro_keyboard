from contextlib import contextmanager
import ctypes
from ctypes import wintypes
import time

"""
This is basically a copy of PyAutoGui's keyboard functions
I just modifided the way it sends key presses

I changed ctypes.windll.user32.keybd_event()  to
user32.SendInput()
because StarCitizen registers keys sent with SendInput() 
and it is also much faster

I might add mouse funtionality in the future
"""


user32 = ctypes.WinDLL('user32', use_last_error=True)

INPUT_MOUSE    = 0
INPUT_KEYBOARD = 1

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP       = 0x0002
KEYEVENTF_UNICODE     = 0x0004
KEYEVENTF_SCANCODE    = 0x0008

MAPVK_VK_TO_VSC = 0

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

keyboardMapping = {
'\t ': 0x09,
'\n': 0x0d,
'\r': 0xd,
' ' : 0x20,
'!' : 0x131,
'"' : 0x1de,
'#' : 0x133,
'$' : 0x134,
'%' : 0x135,
'&' : 0x137,
"'" : 0xde,
'(' : 0x139,
')' : 0x130,
'*' : 0x138,
'+' : 0x1bb,
',' : 0xbc,
'-' : 0xbd,
'.' : 0xbe,
'/' : 0xbf,
'0' : 0x30,
'1' : 0x31,
'2' : 0x32,
'3' : 0x33,
'4' : 0x34,
'5' : 0x35,
'6' : 0x36,
'7' : 0x37,
'8' : 0x38,
'9' : 0x39,
':' : 0x1ba,
';' : 0xba,
'<' : 0x1bc,
'=' : 0xbb,
'>' : 0x1be,
'?' : 0x1bf,
'@' : 0x132,
'[' : 0xdb,
'\\' : 0xdc,
']' : 0xdd,
'^' : 0x136,
'_' : 0x1bd,
'`' : 0xc0,
'a' : 0x41,
'b' : 0x42,
'c' : 0x43,
'd' : 0x44,
'e' : 0x45,
'f' : 0x46,
'g' : 0x47,
'h' : 0x48,
'i' : 0x49,
'j' : 0x4a,
'k' : 0x4b,
'l' : 0x4c,
'm' : 0x4d,
'n' : 0x4e,
'o' : 0x4f,
'p' : 0x50,
'q' : 0x51,
'r' : 0x52,
's' : 0x53,
't' : 0x54,
'u' : 0x55,
'v' : 0x56,
'w' : 0x57,
'x' : 0x58,
'y' : 0x59,
'z' : 0x5a,
'{' : 0x1db,
'|' : 0x1dc,
'}' : 0x1dd,
'~' : 0x1c0,
'accept' : 0x1e,
'add' : 0x6b,
'alt' : 0x12,
'altleft' : 0xa4,
'altright' : 0xa5,
'apps' : 0x5d,
'backspace' : 0x8,
'browserback' : 0xa6,
'browserfavorites' : 0xab,
'browserforward' : 0xa7,
'browserhome' : 0xac,
'browserrefresh' : 0xa8,
'browsersearch' : 0xaa,
'browserstop' : 0xa9,
'capslock' : 0x14,
'clear' : 0xc,
'convert' : 0x1c,
'ctrl' : 0x11,
'ctrlleft' : 0xa2,
'ctrlright' : 0xa3,
'decimal' : 0x6e,
'del' : 0x2e,
'delete' : 0x2e,
'divide' : 0x6f,
'down' : 0x28,
'end' : 0x23,
'enter' : 0xd,
'esc' : 0x1b,
'escape' : 0x1b,
'execute' : 0x2b,
'f1' : 0x70,
'f2' : 0x71,
'f3' : 0x72,
'f4' : 0x73,
'f5' : 0x74,
'f6' : 0x75,
'f7' : 0x76,
'f8' : 0x77,
'f9' : 0x78,
'f10' : 0x79,
'f11' : 0x7a,
'f12' : 0x7b,
'f13' : 0x7c,
'f14' : 0x7d,
'f15' : 0x7e,
'f16' : 0x7f,
'f17' : 0x80,
'f18' : 0x81,
'f19' : 0x82,
'f20' : 0x83,
'f21' : 0x84,
'f22' : 0x85,
'f23' : 0x86,
'f24' : 0x87,
'final' : 0x18,
'fn' : None,
'hanguel' : 0x15,
'hangul' : 0x15,
'hanja' : 0x19,
'help' : 0x2f,
'home' : 0x24,
'insert' : 0x2d,
'junja' : 0x17,
'kana' : 0x15,
'kanji' : 0x19,
'launchapp1' : 0xb6,
'launchapp2' : 0xb7,
'launchmail' : 0xb4,
'launchmediaselect' : 0xb5,
'left' : 0x25,
'modechange' : 0x1f,
'multiply' : 0x6a,
'nexttrack' : 0xb0,
'nonconvert' : 0x1d,
'num0' : 0x60,
'num1' : 0x61,
'num2' : 0x62,
'num3' : 0x63,
'num4' : 0x64,
'num5' : 0x65,
'num6' : 0x66,
'num7' : 0x67,
'num8' : 0x68,
'num9' : 0x69,
'numlock' : 0x90,
'pagedown' : 0x22,
'pageup' : 0x21,
'pause' : 0x13,
'pgdn' : 0x22,
'pgup' : 0x21,
'playpause' : 0xb3,
'prevtrack' : 0xb1,
'print' : 0x2a,
'printscreen' : 0x2c,
'prntscrn' : 0x2c,
'prtsc' : 0x2c,
'prtscr' : 0x2c,
'return' : 0xd,
'right' : 0x27,
'scrolllock' : 0x91,
'select' : 0x29,
'separator' : 0x6c,
'shift' : 0x10,
'shiftleft' : 0xa0,
'shiftright' : 0xa1,
'sleep' : 0x5f,
'space' : 0x20,
'stop' : 0xb2,
'subtract' : 0x6d,
'tab' : 0x9,
'up' : 0x26,
'volumedown' : 0xae,
'volumemute' : 0xad,
'volumeup' : 0xaf,
'win' : 0x5b,
'winleft' : 0x5b,
'winright' : 0x5c,
'yen' : None,
'command' : None,
'option' : None,
'optionleft' : None,
'optionright' : None,
'\b': 0x08,
'super' : 0x5b,
'A' : 0x141,
'B' : 0x142,
'C' : 0x143,
'D' : 0x144,
'E' : 0x145,
'F' : 0x146,
'G' : 0x147,
'H' : 0x148,
'I' : 0x149,
'J' : 0x14a,
'K' : 0x14b,
'L' : 0x14c,
'M' : 0x14d,
'N' : 0x14e,
'O' : 0x14f,
'P' : 0x150,
'Q' : 0x151,
'R' : 0x152,
'S' : 0x153,
'T' : 0x154,
'U' : 0x155,
'V' : 0x156,
'W' : 0x157,
'X' : 0x158,
'Y' : 0x159,
'Z' : 0x15a,
'\x7f' : 0x208}

def isShiftCharacter(character):
    """
    Returns True if the ``character`` is a keyboard key that would require the shift key to be held down, such as
    uppercase letters or the symbols on the keyboard's number row.
    """
    # NOTE TODO - This will be different for non-qwerty keyboards.
    return character.isupper() or character in set('~!@#$%^&*()_+{}|:"<>?')

def keyDown(key):
    """Performs a keyboard key press without the release. This will put that
    key in a held down state.
    Args:
      key (str): The key to be pressed down. The valid names are listed in
      KEYBOARD_KEYS.
    Returns:
      None
    """
    if len(key) > 1:
        key = key.lower()

    if key not in keyboardMapping or keyboardMapping[key] is None:
        msg = f'Key is not Valid: {key}'
        raise SyntaxError(msg)

    needsShift = isShiftCharacter(key)

    mods, vkCode = divmod(keyboardMapping[key], 0x100)

    #print(f'{key=}, {mods=}, {hex(vkCode)=}, {needsShift=}')

    # checks for shift(0x10), ctrl(0x11) and alt(0x12)
    for apply_mod, vk_mod in [(mods & 4, 0x12), (mods & 2, 0x11),
        (mods & 1 or needsShift, 0x10)]: #HANKAKU not supported! mods & 8

        # presses Ctrl, alt or shift
        if apply_mod:
            x = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=vk_mod))
            user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

    #presses main key
    x = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=vkCode))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

    for apply_mod, vk_mod in [(mods & 1 or needsShift, 0x10), (mods & 2, 0x11),
        (mods & 4, 0x12)]: #HANKAKU not supported! mods & 8
        if apply_mod:
            x = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=vk_mod, dwFlags=KEYEVENTF_KEYUP))
            user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

def keyUp(key):
    """Performs a keyboard key release (without the press down beforehand).
    Args:
      key (str): The key to be pressed down. The valid names are listed in
      KEYBOARD_KEYS.
    Returns:
      None
    """
    if len(key) > 1:
        key = key.lower()

    if key not in keyboardMapping or keyboardMapping[key] is None:
        return

    needsShift = isShiftCharacter(key)

    mods, vkCode = divmod(keyboardMapping[key], 0x100)

    # checks for shift(0x10), ctrl(0x11) and alt(0x12)
    for apply_mod, vk_mod in [(mods & 4, 0x12), (mods & 2, 0x11),
        (mods & 1 or needsShift, 0x10)]: #HANKAKU not supported! mods & 8

        # presses Ctrl, alt or shift
        if apply_mod:
            x = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=vk_mod)) # down
            user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

    #releases main key
    x = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=vkCode, dwFlags=KEYEVENTF_KEYUP))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))
    for apply_mod, vk_mod in [(mods & 1 or needsShift, 0x10), (mods & 2, 0x11),
        (mods & 4, 0x12)]: #HANKAKU not supported! mods & 8
        if apply_mod:
            x = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=vk_mod, dwFlags=KEYEVENTF_KEYUP))
            user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

def press(keys, presses=1, interval=0.0):
    """Performs a keyboard key press down, followed by a release.

    Args:
      key (str, list): The key to be pressed. The valid names are listed in
      KEYBOARD_KEYS. Can also be a list of such strings.
      presses (integer, optional): The number of press repetitions.
      1 by default, for just one press.
      interval (float, optional): How many seconds between each press.
      0.0 by default, for no pause between presses.
    Returns:
      None
    """
    if type(keys) == str:
        if len(keys) > 1:
            keys = keys.lower()
        keys = [keys] # If keys is 'enter', convert it to ['enter'].
    else:
        lowerKeys = []
        for s in keys:
            if len(s) > 1:
                lowerKeys.append(s.lower())
            else:
                lowerKeys.append(s)
        keys = lowerKeys

    interval = float(interval)

    for _ in range(presses):
        for k in keys:
            keyDown(k)
            keyUp(k)
        time.sleep(interval)

@contextmanager
def hold(keys):
    """Context manager that performs a keyboard key press down upon entry,
    followed by a release upon exit.

    Args:
      key (str, list): The key to be pressed. The valid names are listed in
      KEYBOARD_KEYS. Can also be a list of such strings.
      pause (float, optional): How many seconds in the end of function process.
      None by default, for no pause in the end of function process.
    Returns:
      None
    """
    if type(keys) == str:
        if len(keys) > 1:
            keys = keys.lower()
        keys = [keys] # If keys is 'enter', convert it to ['enter'].
    else:
        lowerKeys = []
        for s in keys:
            if len(s) > 1:
                lowerKeys.append(s.lower())
            else:
                lowerKeys.append(s)
        keys = lowerKeys
    for k in keys:
        keyDown(k)
    try:
        yield
    finally:
        for k in keys:
            keyUp(k)

def hotkey(*args, **kwargs):
    """Performs key down presses on the arguments passed in order, then performs
    key releases in reverse order.

    The effect is that calling hotkey('ctrl', 'shift', 'c') would perform a
    "Ctrl-Shift-C" hotkey/keyboard shortcut press.

    Args:
      key(s) (str): The series of keys to press, in order. This can also be a
        list of key strings to press.
      interval (float, optional): The number of seconds in between each press.
        0.0 by default, for no pause in between presses.

    Returns:
      None
    """
    interval = float(kwargs.get("interval", 0.0))  # TODO - this should be taken out.

    for c in args:
        if len(c) > 1:
            c = c.lower()
        keyDown(c)
        time.sleep(interval)
    for c in reversed(args):
        if len(c) > 1:
            c = c.lower()
        keyUp(c)
        time.sleep(interval)
