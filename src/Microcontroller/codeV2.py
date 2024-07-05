import time
import board
import neopixel
from rainbowio import colorwheel

"""
This works YAYAYAYY


"""


# pixel_pin = board.RX
# num_pixels = 15
# pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.1, auto_write=False)

# def rainbow_cycle(wait):
#     for j in range(255):
#         for i in range(num_pixels):
#             rc_index = (i * 256 // num_pixels) + j
#             pixels[i] = colorwheel(rc_index & 255)
#         pixels.show()
#         time.sleep(wait)

# while True:
#     rainbow_cycle(0)
# import neopixel
import keypad
import board
import rotaryio
import digitalio
import supervisor
import time

encoder_1_button = digitalio.DigitalInOut(board.D8)
encoder_1_button.direction = digitalio.Direction.INPUT
encoder_1_button.pull = digitalio.Pull.UP
encoder_1_button_state = None
encoder_1 = rotaryio.IncrementalEncoder(board.D4, board.D5)
encoder_1_last_position = 0


encoder_2_button = digitalio.DigitalInOut(board.D9)
encoder_2_button.direction = digitalio.Direction.INPUT
encoder_2_button.pull = digitalio.Pull.UP
encoder_2_button_state = None
encoder_2 = rotaryio.IncrementalEncoder(board.D6, board.D7)
encoder_2_last_position = 0


keys = keypad.KeyMatrix(
    row_pins=(board.A3, board.D2, board.D3),
    column_pins=(board.D10, board.A0, board.A1, board.A2),
    columns_to_anodes=True,
    max_events = 10
)


#doesnt work, because I put a diode infront of  it, so current doesnt pass trhought it.
# Bridged the connection and now it works.
ModeButton = keypad.Keys((board.TX,), value_when_pressed=False, pull=True)
Mode = 1

# will need to re wire  alll the leds, looks like the schematic for the leds were all wrong, So i probably fried 15 of them.
# put a 330 ohm resiston going into data in line for LED

#Neo Pixel stuff
#https://learn.adafruit.com/adafruit-neopixel-uberguide/python-circuitpython
# https://learn.adafruit.com/getting-started-with-raspberry-pi-pico-circuitpython/neopixel-leds


# led = digitalio.DigitalInOut(board.NEOPIXEL)
# led.direction = digitalio.Direction.OUTPUT

pixel_pin = board.RX
num_pixels = 15
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.1, auto_write=False)



#key_names = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'A', 'B', 'ModeButton']
held_keys = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

def msgContructor(event, type, encoder_button: int = 0, encoder_pos_change: int = 0 ):

    if type == "mode": 
        #check if it has a timestamp and if diff <(less then) 0.250:  then send: 00010000 (0001 = release 0000 = mode)
        
        if held_keys[-1] != 0:  # I dont think this needs to be here
    
            diff = (supervisor.ticks_ms() - held_keys[-1])/1000
            if diff < 0.250:   # if its less then
                type_bits = '0000'
                action_bits = '0001'
            else:
                held_keys[-1]  = 0
                return 

        held_keys[-1]  = 0

    elif type == "rotary encoder": #look at the encoder vars list, which would be ordered as ["name", ChangeInPosition, buttonState],  

        if event == "Encoder1":
            type_bits = 1110   #(14)
        elif event == "Encoder2":
            type_bits = 1111   #(15)

        # the button value in binary
        bit2 = int(encoder_button)

        # 0 for left and 1 for right,   left is negative and right is positive
        bit4 = int(encoder_pos_change > 0)

        action_bits = f"0{bit2}1{bit4}"
        #0010: rotary left w/o button
        #0011: rotary right w/o button

        #0110: rotary left w/ button
        #0111: rotary right w/ button 

    elif type == "button":
        key_timestamp = held_keys[MatrixEvent.key_number]

        if key_timestamp != 0:
            diff = (supervisor.ticks_ms() - key_timestamp) /1000
            
            if diff < 0.250: # this means it was pressed fast
                # type_bits = bin(MatrixEvent.key_number+1)
                type_bits = f'{MatrixEvent.key_number+1:04b}'
                action_bits = '0001'

            else: # the buton was held for over 0.250 seconds 
                held_keys[MatrixEvent.key_number]  = 0
                return

        held_keys[MatrixEvent.key_number]  = 0
      
    msg = f"{action_bits}{type_bits}"

    # on to layers now      
    for i in held_keys:

        if i != 0:
            #if there is a button  that is being held

            diff = (supervisor.ticks_ms() - i)/1000
            if diff > 0.100: 
                held_key_index = held_keys.index(i)
                if held_key_index == 12:
                    type_bits = "0000"
                else:
                    type_bits = f'{held_key_index+1:04b}'

                msg = type_bits+msg

    print(msg)
    pixels[14] = (0, 255, 0)
    pixels.show()
    #time.sleep(0.05)
    pixels[14] = (0, 0, 0)
    pixels.show()
    

while True:
    #  Encoder Stuff
    encoder_1_position = encoder_1.position
    encoder_2_position = encoder_2.position
    if encoder_1_last_position is None or encoder_1_position != encoder_1_last_position:
        # led.value = True
        encoder_1_position_change = encoder_1_position - encoder_1_last_position

        msgContructor("Encoder1", "rotary encoder", not encoder_1_button.value, encoder_1_position_change)
        time.sleep(0.1)
        # led.value = False


    encoder_1_last_position = encoder_1_position

    if encoder_2_last_position is None or encoder_2_position != encoder_2_last_position:
        # led.value = True
        encoder_2_position_change = encoder_2_position -  encoder_2_last_position

        msgContructor("Encoder2", "rotary encoder", not encoder_2_button.value, encoder_2_position_change)
        time.sleep(0.1)
        # led.value = False


    encoder_2_last_position = encoder_2_position

    # if not encoder_1_button.value and encoder_1_button_state is None:
    #     encoder_1_button_state = "pressed"
    #     print("Button pressed.")
    # if encoder_1_button.value and encoder_1_button_state == "pressed":
    #     print("Button released.")
    #     encoder_1_button_state = None

    if MatrixEvent := keys.events.get():
        # this is the main 4x3 key grid.
        
        if MatrixEvent.pressed:
            # when the button is pressed, all I want it to do is put the time stamp in he held_keys list 
            # led.value = True
            held_keys[MatrixEvent.key_number]  = MatrixEvent.timestamp
            
            ### A barebones test for changing colors if its a layer
            pixels[MatrixEvent.key_number] = (255, 0, 0)
            pixels.show()
            for i in held_keys:
                if i != 0:
                    #if there is a button  that is being held

                    diff = (supervisor.ticks_ms() - i)/1000
                    if diff > 0.100: 
                        pixels[held_keys.index(i)] = (255,255,0)
                        pixels.show()


        if MatrixEvent.released:
            # led.value = False
            msgContructor(MatrixEvent, 'button')
            
            pixels[MatrixEvent.key_number] = (0, 0, 0)
            pixels.show()

    if ModeEvent := ModeButton.events.get():
        # this is the mode buttons
        if ModeEvent.pressed:
            pixels[14] = (255, 0, 0)
            pixels.show()
            # led.value = True
            held_keys[-1]  = ModeEvent.timestamp

        if ModeEvent.released:
            # led.value = False
            msgContructor(ModeEvent, "mode")
            pixels[14] = (0, 0, 0)
            pixels.show()