#this will be the new code for thee Pi Pico based Macro

"""TODO:
2. multi button presses to work   

For multi keys to work, Ill probably have to move the send action stuff to when the key is released.

Have a list of 12 0, then when a button is pressed, put the timestamp of the key in the list.
If it is released, make the item at index[key_num] 0

After the if MatrixEvent := keys.events.get(): and the mode button one

Check if actions has something in it.
if it does have code that will get the current timestamp, and look in the list for anything thats not 0

dif = now - before
if dif > 0.50:

then add 

msg = {
        "Event": key_name,
        "isBeingHeld": True,
        "Mode": Mode,
    }          
actions.append(msg)



3. then figure out how to communicate with driver and make a new driver version to   work with it, take improvements from the not implemented driver version
"Event": "Encoder1",
"Position": encoder_1_position,
"ChangeInPosition": encoder_1_position_change,
"isButtonPressed": not encoder_1_button.value,
"Mode": Mode,
"isBeingHeld": True

I will have to make something that will interpret all those and that will allow for multiple actions at once

"""

import neopixel
import keypad
import board
import rotaryio
import digitalio

# try both encoders, at the same time
# currently the encoder must be pressed down and spun for it to control audio, I want that feature to be used to control spotify volume  and song scrubbing.



encoder_1_button = digitalio.DigitalInOut(board.GP17)
encoder_1_button.direction = digitalio.Direction.INPUT
encoder_1_button.pull = digitalio.Pull.UP
encoder_1_button_state = None
encoder_1 = rotaryio.IncrementalEncoder(board.GP20, board.GP21)
encoder_1_last_position = 0


encoder_2_button = digitalio.DigitalInOut(board.GP16)
encoder_2_button.direction = digitalio.Direction.INPUT
encoder_2_button.pull = digitalio.Pull.UP
encoder_2_button_state = None
encoder_2 = rotaryio.IncrementalEncoder(board.GP18, board.GP19)
encoder_2_last_position = 0



keys = keypad.KeyMatrix(
    row_pins=(board.GP2, board.GP3, board.GP4),
    column_pins=(board.GP9, board.GP8, board.GP7, board.GP6),
    columns_to_anodes=True,
    max_events = 10
)


#doesnt work, because I put a diode infront of  it, so current doesnt pass trhought it.
# Birdged the connection and now it works.
ModeButton = keypad.Keys((board.GP0,), value_when_pressed=False, pull=True)


# will need to re wire  alll the leds, looks like the schematic for the leds were all wrong, So i probably fried 15 of them.
# put a 330 ohm resiston going into data in line for LED

#Neo Pixel stuff
#https://learn.adafruit.com/adafruit-neopixel-uberguide/python-circuitpython
Mode = 1
# MODELEDVALUES = [(0, 255, 0), (0, 0, 255), (0, 255, 255), (255, 0, 0)]
OFF_COLOR = (0, 255, 0)
ON_COLOR = (255, 0, 255)
onBoardLED = neopixel.NeoPixel(board.GP25, 1, brightness=1)

key_names = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'A',  'B']

while True:
    # actions = {
    #     "Event": "",
    #     "Value": "",
    # }
    actions = []

    #  Encoder Stuff

    encoder_1_position = encoder_1.position
    encoder_2_position = encoder_2.position
    if encoder_1_last_position is None or encoder_1_position != encoder_1_last_position:
        encoder_1_position_change = encoder_1_position -  encoder_1_last_position

        #msg = f"Encoder1Pos: {encoder_1_position}, Encoder1PosChange: {encoder_1_position_change}, isButtonPressed: {not encoder_1_button.value}"
        #print(msg) 
        msg = {
            "Event": "Encoder1",
            "Position": encoder_1_position,
            "ChangeInPosition": encoder_1_position_change,
            "isButtonPressed": not encoder_1_button.value,
            "Mode": Mode
            }

        actions.append(msg)

    encoder_1_last_position = encoder_1_position

    if encoder_2_last_position is None or encoder_2_position != encoder_2_last_position:
        encoder_2_position_change = encoder_2_position -  encoder_2_last_position

        # msg = f"Encoder2Pos: {encoder_2_position}, Encoder2PosChange: {encoder_2_position_change}, isButtonPressed: {not encoder_2_button.value}"
        # print(msg)

        msg = {
            "Event": "Encoder2",
            "Position": encoder_2_position,
            "ChangeInPosition": encoder_2_position_change,
            "isButtonPressed": not encoder_2_button.value,
            "Mode": Mode
            }

        actions.append(msg)

    encoder_2_last_position = encoder_2_position

    # if not encoder_1_button.value and encoder_1_button_state is None:
    #     encoder_1_button_state = "pressed"
    #     print("Button pressed.")
    # if encoder_1_button.value and encoder_1_button_state == "pressed":
    #     print("Button released.")
    #     encoder_1_button_state = None


    # Key stuff

    if MatrixEvent := keys.events.get():
        if MatrixEvent.pressed:

            onBoardLED[0] = ON_COLOR
            new_key_name = key_names[int(MatrixEvent.key_number)]

            #print(f"Button {new_key_name}.{Mode}")

            msg = {
                "Event": new_key_name,
                "isButtonPressed": MatrixEvent.pressed,
                "Mode": Mode,
            }                
            actions.append(msg)

        if MatrixEvent.released:
            onBoardLED[0] = OFF_COLOR

    if ModeEvent := ModeButton.events.get():
        if ModeEvent.pressed:

            onBoardLED[0] = ON_COLOR

            if Mode == 4:
                Mode = 1
            else:
                Mode  += 1
            #print(f"mode button was pressed   macro button is : {Mode}")

            msg = {
                "Event": "ModeButton",
                "isButtonPressed": ModeEvent.pressed,
                "Mode": Mode,
            } 
            actions.append(msg)

        if ModeEvent.released:
            onBoardLED[0] = OFF_COLOR

    if actions:
        print(actions) 