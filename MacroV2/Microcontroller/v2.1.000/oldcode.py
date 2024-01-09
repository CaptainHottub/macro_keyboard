import time

# import keypad
import board


# import neopixel

import rotaryio
import digitalio
import usb_hid
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

button_1 = digitalio.DigitalInOut(board.GP17)
button_1.direction = digitalio.Direction.INPUT
button_1.pull = digitalio.Pull.UP

#encoder1 = rotaryio.IncrementalEncoder(board.GP21, board.GP20)

cc = ConsumerControl(usb_hid.devices)

# button_state = None
# last_position1 = encoder1.position

# while True:
#     current_position1 = encoder1.position
    
#     position_change1 = current_position1 - last_position1
#     print(current_position1, position_change1)
#     #measures the change in position, 
#     if position_change1 > 0:
#         for _ in range(position_change1):
#             cc.send(ConsumerControlCode.VOLUME_INCREMENT)
#         print(current_position1)
#     elif position_change1 < 0:
#         for _ in range(-position_change1):
#             cc.send(ConsumerControlCode.VOLUME_DECREMENT)
#         print(current_position1)
#     last_position = current_position1
    
#     if not button.value and button_state is None:
#         button_state = "pressed"
#     if button.value and button_state == "pressed":
#         print("Button pressed.")
#         cc.send(ConsumerControlCode.PLAY_PAUSE)
#         button_state = None

# try both encoders, at the same time
# currently the encoder must be pressed down and spun for it to control audio, I want that feature to be used to control spotify volume  and song scrubbing.
encoder_1_button_state = None
encoder_1 = rotaryio.IncrementalEncoder(board.GP20, board.GP21)
encoder_1_last_position = 0
while True:
    encoder_1_position = encoder_1.position
    #measures the raw encoder position
    if encoder_1_last_position is None or encoder_1_position != encoder_1_last_position:

        encoder_1_position_change = encoder_1_position -  encoder_1_last_position
        
        if encoder_1_position_change > 0 and not button_1.value:
            for _ in range(encoder_1_position_change):
                cc.send(ConsumerControlCode.VOLUME_INCREMENT)
            print(encoder_1_position)
        
        elif encoder_1_position_change < 0 and not button_1.value:
            for _ in range(-encoder_1_position_change):
                cc.send(ConsumerControlCode.VOLUME_DECREMENT)
            print(encoder_1_position)

        # Encoder position, true is button is pressed
        print(encoder_1_position, not button_1.value)
    encoder_1_last_position = encoder_1_position

    if not button_1.value and encoder_1_button_state is None:
        encoder_1_button_state = "pressed"
        print("Button pressed.")
    if button_1.value and encoder_1_button_state == "pressed":
        print("Button released.")
        #cc.send(ConsumerControlCode.PLAY_PAUSE)
        encoder_1_button_state = None


        








#  Try and get multi button presses to work,  then  try and have the encoders work with it
#  then figure out how to communicate with driver and make a new driver version to   work with it, take improvements from the not implemented driver version
        

# keys = keypad.KeyMatrix(
#     row_pins=(board.GP2, board.GP3, board.GP4),
#     column_pins=(board.GP9, board.GP8, board.GP7, board.GP6)
# )


# #doesnt work, because I put a diode infront of  it, so current doesnt pass trhought it.
# # Birdged the connection and now it works.
# ModeButton = keypad.Keys((board.GP0,), value_when_pressed=False, pull=True)


# # will need to re wire  alll the leds, looks like the schematic for the leds were all wrong, So i probably fried 15 of them.
# # put a 330 ohm resiston going into data in line for LED

# #Neo Pixel stuff
# #https://learn.adafruit.com/adafruit-neopixel-uberguide/python-circuitpython
# Mode = 1
# # MODELEDVALUES = [(0, 255, 0), (0, 0, 255), (0, 255, 255), (255, 0, 0)]
# OFF_COLOR = (0, 255, 0)
# ON_COLOR = (255, 0, 255)
# # ModeButtonLED = neopixel.NeoPixel(board.D1, 1, brightness=0.4)
# # ModeButtonLED.fill(OFF_COLOR)
# STANDY_COLOR = (255, 255, 255)
# ledMatrix = neopixel.NeoPixel(board.GP1, 15, brightness=1)
# ledMatrix.fill(STANDY_COLOR)


# key_names = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'A',  'B']


# while True:
#     if MatrixEvent := keys.events.get():
#         if MatrixEvent.pressed:
#             ledMatrix[1] = ON_COLOR
#             #ModeButtonLED[0] = ON_COLOR
#             new_key_name = key_names[int(MatrixEvent.key_number)]

#             print(f"Button {new_key_name}.{Mode}")
#         if MatrixEvent.released:
#             ledMatrix[0] = OFF_COLOR

#             # ledMatrix[int(MatrixEvent.key_number)] = OFF_COLOR
#             #ModeButtonLED[0] = OFF_COLOR

#     if ModeEvent := ModeButton.events.get():
#         if ModeEvent.pressed:
            
#             # onBoardLED[0] = ON_COLOR
            
#             if Mode == 4:
#                 Mode = 1
#             else:
#                 Mode  += 1
#             print(f"mode button was pressed   macro button is : {Mode}")
#             #ModeButtonLED[event.key_number] = ON_COLOR
            
#             #print("Mode Button, mode button was pressed")

#             # ModeButtonLED.fill(MODELEDVALUES[Mode])

#         # if ModeEvent.released:
#         #     onBoardLED[0] = OFF_COLOR
#         #     ModeButtonLED[ModeEvent.key_number] = MODELEDVALUES[Mode]
       
#         # Mode Button, mode button was pressed





















# while True:
#     if MatrixEvent := keys.events.get():
#         if MatrixEvent.pressed:
#             #ledMatrix[0] = ON_COLOR
#             #ModeButtonLED[0] = ON_COLOR
#             new_key_name = key_names[int(MatrixEvent.key_number)]

#             print(f"Button {new_key_name}.{Mode}")
#         #if MatrixEvent.released:
#             #ledMatrix[0] = OFF_COLOR

#             # ledMatrix[int(MatrixEvent.key_number)] = OFF_COLOR
#             #ModeButtonLED[0] = OFF_COLOR

#     if ModeEvent := ModeButton.events.get():
#         if ModeEvent.pressed:
            
#             # onBoardLED[0] = ON_COLOR
            
#             if Mode == 4:
#                 Mode = 1
#             else:
#                 Mode  += 1
#             print(f"mode button was pressed   macro button is : {Mode}")
#             #ModeButtonLED[event.key_number] = ON_COLOR
            
#             #print("Mode Button, mode button was pressed")

#             # ModeButtonLED.fill(MODELEDVALUES[Mode])

#         # if ModeEvent.released:
#         #     onBoardLED[0] = OFF_COLOR
#         #     ModeButtonLED[ModeEvent.key_number] = MODELEDVALUES[Mode]
       
#         # Mode Button, mode button was pressed


# #     # event = keys.events.get()
# #     # if event:
# #     #     key_number = event.key_number
# #     #     # A key transition occurred.
# #     #     if event.pressed:
# #     #         print(event)
           
# #             #neopixels[key_number] = ON_COLOR
# #     #     if event.released:
# #     #         print(event)
# #             #neopixels[key_number] = OFF_COLOR
# #     if event := keys.events.get():
# #         if event.pressed:
# #             onBoardLED[0] = ON_COLOR
# #             # ModeButtonLED[0] = ON_COLOR
# #             new_key_name = key_names[int(event.key_number)]

# #             print(f"Button {new_key_name}")
# #         if event.released:
# #             onBoardLED[0] = OFF_COLOR
# #         #     ModeButtonLED[0] = MODELEDVALUES[Mode]

# #     if event := ModeButton.events.get():
# #         if event.pressed:
# #             #ModeButtonLED[event.key_number] = ON_COLOR
# #             print("Mode Button, mode button was pressed")

            
# #             # if Mode == 3:
# #             #     Mode = 0
# #             # else:
# #             #     Mode  += 1
    
# #             # ModeButtonLED.fill(MODELEDVALUES[Mode])

# #         # if event.released:
# #         #     ModeButtonLED[event.key_number] = MODELEDVALUES[Mode]
       
# #         # Mode Button, mode button was pressed

