# import neopixel
import keypad
import board
import rotaryio
import digitalio
import supervisor
import time

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
# Bridged the connection and now it works.
ModeButton = keypad.Keys((board.GP0,), value_when_pressed=False, pull=True)
Mode = 1

# will need to re wire  alll the leds, looks like the schematic for the leds were all wrong, So i probably fried 15 of them.
# put a 330 ohm resiston going into data in line for LED

#Neo Pixel stuff
#https://learn.adafruit.com/adafruit-neopixel-uberguide/python-circuitpython
# https://learn.adafruit.com/getting-started-with-raspberry-pi-pico-circuitpython/neopixel-leds


led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

###################### TEST #####################
event_name_to_bits = {
    'Encoder1': 1110,
    'Encoder2': 1111}

def encoderMsgBuilder(encoder, button_val, pos_change):
    encoder_bits = event_name_to_bits[encoder]

    # button_val is a bool, so I can take the int value of that and use it as a bit
    bit2 = int(button_val)

    # true if greater, false if not
    bit4 = int(pos_change > 0)
    
    event_type_byte = f"0{bit2}1{bit4}"

    byte_msg =  f"{event_type_byte}{encoder_bits}"
    print(byte_msg)


def buttonMsgBuilder(event, event_type):
    key_num = event.key_number
    is_pressed = event.pressed

    if event_type == 'button':
        key_num += 1
    
    # turns the number into binary
    key_num_byte = f'{key_num:04b}'

    # '0000' for pressed and '0001' for released
    event_type_byte = '0000' if is_pressed else '0001'

    byte_msg =  f"{event_type_byte}{key_num_byte}"
    print(byte_msg)

while True:
    #  Encoder Stuff
    encoder_1_position = encoder_1.position
    encoder_2_position = encoder_2.position
    if encoder_1_last_position is None or encoder_1_position != encoder_1_last_position:
        led.value = True
        encoder_1_position_change = encoder_1_position - encoder_1_last_position

        encoderMsgBuilder("Encoder1", not encoder_1_button.value, encoder_1_position_change)
        time.sleep(0.1)
        led.value = False
    
    encoder_1_last_position = encoder_1_position

    if encoder_2_last_position is None or encoder_2_position != encoder_2_last_position:
        led.value = True
        encoder_2_position_change = encoder_2_position -  encoder_2_last_position
        
        encoderMsgBuilder("Encoder2", not encoder_2_button.value, encoder_2_position_change)
        time.sleep(0.1)
        led.value = False

    encoder_2_last_position = encoder_2_position

    # if not encoder_1_button.value and encoder_1_button_state is None:
    #     encoder_1_button_state = "pressed"
    #     print("Button pressed.")
    # if encoder_1_button.value and encoder_1_button_state == "pressed":
    #     print("Button released.")
    #     encoder_1_button_state = None

    if MatrixEvent := keys.events.get():
        # this is the main 4x3 key grid.
        
        buttonMsgBuilder(MatrixEvent, 'button')
        if MatrixEvent.pressed:
            led.value = True

        elif MatrixEvent.released:
            led.value = False

    if ModeEvent := ModeButton.events.get():
        # this is the mode buttons

        buttonMsgBuilder(ModeEvent, 'mode')
        if ModeEvent.pressed:
            led.value = True

        elif ModeEvent.released:
            led.value = False
        