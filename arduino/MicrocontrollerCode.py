import time

import keypad
import board
import neopixel

keys = keypad.KeyMatrix(
    row_pins=(board.D4, board.D5, board.A3),
    column_pins=(board.D6, board.D7, board.D8, board.D9),
)

ModeButton = keypad.Keys((board.A0,), value_when_pressed=False, pull=True)


#Neo Pixel stuff
#https://learn.adafruit.com/adafruit-neopixel-uberguide/python-circuitpython
Mode = 1
# MODELEDVALUES = [(0, 255, 0), (0, 0, 255), (0, 255, 255), (255, 0, 0)]

# ON_COLOR = (255, 0, 255)
# ModeButtonLED = neopixel.NeoPixel(board.A2, 1, brightness=0.4)
# ModeButtonLED.fill(MODELEDVALUES[Mode])


#ON_COLOR = (0, 0, 255)
#OFF_COLOR = (0, 20, 0)

ON_COLOR = (255, 0, 0)
OFF_COLOR = (0, 0, 0)
onBoardLED = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.1)
onBoardLED.fill(OFF_COLOR)




key_names = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'A',  'B']

while True:
    if MatrixEvent := keys.events.get():
        if MatrixEvent.pressed:
            onBoardLED[0] = ON_COLOR
            # ModeButtonLED[0] = ON_COLOR
            new_key_name = key_names[int(MatrixEvent.key_number)]

            print(f"Button {new_key_name}.{Mode}")
        if MatrixEvent.released:
            onBoardLED[0] = OFF_COLOR
        #     ModeButtonLED[0] = MODELEDVALUES[Mode]

    if ModeEvent := ModeButton.events.get():
        if ModeEvent.pressed:
            onBoardLED[0] = ON_COLOR
            
            if Mode == 4:
                Mode = 1
            else:
                Mode  += 1

            #ModeButtonLED[event.key_number] = ON_COLOR
            print(f"mode button was pressed   macro button is : {Mode}")
            #print("Mode Button, mode button was pressed")

            
            
    
            # ModeButtonLED.fill(MODELEDVALUES[Mode])

        if ModeEvent.released:
            onBoardLED[0] = OFF_COLOR
            #ModeButtonLED[ModeEvent.key_number] = MODELEDVALUES[Mode]
       
        # Mode Button, mode button was pressed


#     # event = keys.events.get()
#     # if event:
#     #     key_number = event.key_number
#     #     # A key transition occurred.
#     #     if event.pressed:
#     #         print(event)
           
#             #neopixels[key_number] = ON_COLOR
#     #     if event.released:
#     #         print(event)
#             #neopixels[key_number] = OFF_COLOR
#     if event := keys.events.get():
#         if event.pressed:
#             onBoardLED[0] = ON_COLOR
#             # ModeButtonLED[0] = ON_COLOR
#             new_key_name = key_names[int(event.key_number)]

#             print(f"Button {new_key_name}")
#         if event.released:
#             onBoardLED[0] = OFF_COLOR
#         #     ModeButtonLED[0] = MODELEDVALUES[Mode]

#     if event := ModeButton.events.get():
#         if event.pressed:
#             #ModeButtonLED[event.key_number] = ON_COLOR
#             print("Mode Button, mode button was pressed")

            
#             # if Mode == 3:
#             #     Mode = 0
#             # else:
#             #     Mode  += 1
    
#             # ModeButtonLED.fill(MODELEDVALUES[Mode])

#         # if event.released:
#         #     ModeButtonLED[event.key_number] = MODELEDVALUES[Mode]
       
#         # Mode Button, mode button was pressed

