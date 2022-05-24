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

#--- Key Code Variables ---#
class key:
    cancel = 0x03
    backspace = 0x08
    tab = 0x09
    enter = 0x0D
    shift = 0x10
    ctrl = 0x11
    alt = 0x12
    capslock = 0x14
    esc = 0x1B
    space = 0x20
    pgup = 0x21
    pgdown = 0x22
    end = 0x23
    home = 0x24
    leftarrow = 0x26
    uparrow = 0x26
    rightarrow = 0x27
    downarrow = 0x28
    select = 0x29
    print = 0x2A
    execute = 0x2B
    printscreen = 0x2C
    insert = 0x2D
    delete = 0x2E
    help = 0x2F
    num0 = 0x30
    num1 = 0x31
    num2 = 0x32
    num3 = 0x33
    num4 = 0x34
    num5 = 0x35
    num6 = 0x36
    num7 = 0x37
    num8 = 0x38
    num9 = 0x39
    a = 0x41
    b = 0x42
    c = 0x43
    d = 0x44
    e = 0x45
    f = 0x46
    g = 0x47
    h = 0x48
    i = 0x49
    j = 0x4A
    k = 0x4B
    l = 0x4C
    m = 0x4D
    n = 0x4E
    o = 0x4F
    p = 0x50
    q = 0x51
    r = 0x52
    s = 0x53
    t = 0x54
    u = 0x55
    v = 0x56
    w = 0x57
    x = 0x58
    y = 0x59
    z = 0x5A
    leftwin = 0x5B
    rightwin = 0x5C
    apps = 0x5D
    sleep = 0x5F
    numpad0 = 0x60
    numpad1 = 0x61
    numpad3 = 0x63
    numpad4 = 0x64
    numpad5 = 0x65
    numpad6 = 0x66
    numpad7 = 0x67
    numpad8 = 0x68
    numpad9 = 0x69
    multiply = 0x6A
    add = 0x6B
    seperator = 0x6C
    subtract = 0x6D
    decimal = 0x6E
    divide = 0x6F
    F1 = 0x70
    F2 = 0x71
    F3 = 0x72
    F4 = 0x73
    F5 = 0x74
    F6 = 0x75
    F7 = 0x76
    F8 = 0x77
    F9 = 0x78
    F10 = 0x79
    F11 = 0x7A
    F12 = 0x7B
    F13 = 0x7C
    F14 = 0x7D
    F15 = 0x7E
    F16 = 0x7F
    F17 = 0x80
    F19 = 0x82
    F20 = 0x83
    F21 = 0x84
    F22 = 0x85
    F23 = 0x86
    F24 = 0x87
    numlock = 0x90
    scrolllock = 0x91
    leftshift = 0xA0
    rightshift = 0xA1
    leftctrl = 0xA2
    rightctrl = 0xA3
    leftmenu = 0xA4
    rightmenu = 0xA5
    browserback = 0xA6
    browserforward = 0xA7
    browserrefresh = 0xA8
    browserstop = 0xA9
    browserfavories = 0xAB
    browserhome = 0xAC
    volumemute = 0xAD
    volumedown = 0xAE
    volumeup = 0xAF
    nexttrack = 0xB0
    prevoustrack = 0xB1
    stopmedia = 0xB2
    playpause = 0xB3
    launchmail = 0xB4
    selectmedia = 0xB5
    launchapp1 = 0xB6
    launchapp2 = 0xB7
    semicolon = 0xBA
    equals = 0xBB
    comma = 0xBC
    dash = 0xBD
    period = 0xBE
    slash = 0xBF
    accent = 0xC0
    openingsquarebracket = 0xDB
    backslash = 0xDC
    closingsquarebracket = 0xDD
    quote = 0xDE
    play = 0xFA
    zoom = 0xFB
    PA1 = 0xFD
    clear = 0xFE

#--- Keyboard Control Functions ---#

# Category variables
letters = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
shiftsymbols = "~!@#$%^&*()_+QWERTYUIOP{}|ASDFGHJKL:\"ZXCVBNM<>?"


# Functions
user32_2 = ctypes.windll.user32

def HotKey(*hexKeyCodes):
    
    print(hexKeyCodes)
    print(key("numpad7"))

    #pass

def PressKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode, dwFlags=KEYEVENTF_KEYUP))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))


def SendKey(hexKeyCode):
    x1 = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode))
    x2 = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode, dwFlags=KEYEVENTF_KEYUP))
   
    user32.SendInput(1, ctypes.byref(x1), ctypes.sizeof(x1))
    time.sleep(0.2)
    user32.SendInput(1, ctypes.byref(x2), ctypes.sizeof(x2))

