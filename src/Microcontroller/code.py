"""
Listens to the REPL port, without using the usb_cdc module.
Receives color information and displays it on the NEOPIXEL.
Receives blink command and blinks once.
Sends button press and release.

https://github.com/Neradoc/circuitpython-sample-scripts/blob/main/usb_serial/README.md
https://github.com/Neradoc/circuitpython-sample-scripts/blob/main/usb_serial/serial_exchange_repl-code.py
"""

import board
import digitalio
import json
import time
import supervisor
import sys
import keypad
import neopixel
import rotaryio
################################################################
# select the serial REPL port
################################################################

serial = sys.stdin

################################################################
# init board's LEDs for visual output
# replace with your own pins and stuff
################################################################
onboard_pix = neopixel.NeoPixel(board.NEOPIXEL, 1)

pixel_pin = board.RX
num_pixels = 15
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.1, auto_write=False)



encoder_1_button = digitalio.DigitalInOut(board.D8)
encoder_1_button.direction = digitalio.Direction.INPUT
encoder_1_button.pull = digitalio.Pull.UP
encoder_1_button_state = None
#encoder_1 = rotaryio.IncrementalEncoder(board.D4, board.D5)
encoder_1 = rotaryio.IncrementalEncoder(board.D5, board.D4)
encoder_1_last_position = 0


encoder_2_button = digitalio.DigitalInOut(board.D9)
encoder_2_button.direction = digitalio.Direction.INPUT
encoder_2_button.pull = digitalio.Pull.UP
encoder_2_button_state = None
#encoder_2 = rotaryio.IncrementalEncoder(board.D6, board.D7)
encoder_2 = rotaryio.IncrementalEncoder(board.D7, board.D6)
encoder_2_last_position = 0


keys = keypad.KeyMatrix(
    row_pins=(board.A3, board.D2, board.D3),
    column_pins=(board.D10, board.A0, board.A1, board.A2),
    columns_to_anodes=True,
    max_events = 10
)

ModeButton = keypad.Keys((board.TX,), value_when_pressed=False, pull=True)
Mode = 1

held_keys = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

def msgContructor2(event, type, encoder_button: int = 0, encoder_pos_change: int = 0 ):
    data_out = {}
    # data_out["buttons"] = [{"status": "RELEASED", "id": button_id}]
    if type == "mode": 
        #check if it has a timestamp and if diff <(less then) 0.250:  then send: 00010000 (0001 = release 0000 = mode)

        if held_keys[-1]:  # I dont think this needs to be here
    
            diff = (supervisor.ticks_ms() - held_keys[-1])/1000
            if diff < 0.250:   # if its less then
                # data_out["buttons"] = [{"id": hex(0)}]
                # data_out["buttons"] = [{"id": '0x0'}]
                # data_out["button_id"] =  '0x0'
                data_out["Button_id"] =  'Mode'
            else:
                held_keys[-1]  = 0
                return 

        held_keys[-1]  = 0
    
    elif type == "button":
        key_timestamp = held_keys[MatrixEvent.key_number]

        if key_timestamp:
            diff = (supervisor.ticks_ms() - key_timestamp) /1000
            
            if diff < 0.250: # this means it was pressed fast
                # button_id = hex(MatrixEvent.key_number+1)
                # data_out["buttons"] = [{"id": button_id}]
                # data_out["button_id"] = button_id
                data_out["Button_id"] = MatrixEvent.key_number+1

            else: # the buton was held for over 0.250 seconds 
                held_keys[MatrixEvent.key_number]  = 0
                return

        held_keys[MatrixEvent.key_number]  = 0
    
    elif type == "rotary encoder": #look at the encoder vars list, which would be ordered as ["name", ChangeInPosition, buttonState],  
        # print(encoder_pos_change > 0)
        # print(encoder_pos_change, encoder_button)
        
        # encoder = hex(event[-1])
        encoder = int(event[-1])
        # 0 for left and 1 for right,  left is negative and right is positive
        if encoder_pos_change < 0:
            encoder_val = "RL"
        else:
            encoder_val = "RR"
        if encoder_button:
            encoder_val+="B"
        
        data_out["Encoder"] = [{'Id': encoder, 'Value': encoder_val}]
    
    layers = []
    #on to layers now      
    for index, timestamp in enumerate(held_keys):
        if timestamp:
            #if there is a button  that is being held
            diff = (supervisor.ticks_ms() - timestamp)/1000
            if diff > 0.100: 
                if index == 12:
                    # button_id = '0x0'
                    button_id = 'Mode'
                else:
                    # button_id = hex(index+1)
                    button_id = index+1
                layers.append(button_id)

    if len(layers) !=0:
        data_out["Layers"] = layers 
    print(json.dumps(data_out))
    
    pixels[14] = (0, 255, 0)
    pixels.show()
    time.sleep(0.05)
    pixels[14] = (0, 0, 0)
    pixels.show()


################################################################
# loop-y-loop
################################################################

while True:
    # add to that dictionary to send the data at the end of the loop
    # data_out = {}

    ################################################################
    # Data sent from computer
    ################################################################
    # read the REPL serial line by line when there's data
    if supervisor.runtime.serial_bytes_available:
        data_in = serial.readline()

        # try to convert the data to a dict (with JSON)
        data = None
        if len(data_in) > 0:
            try:
                data = json.loads(data_in)
            except ValueError:
                data = {"raw": data_in}

        
        # interpret
        if isinstance(data, dict):
            onboard_pix.fill((0, 255, 0))
            
            if "color" in data:
                color_data = data["color"]
                if color_data[0] == 'All':
                    pixels.fill(color_data[1])
                else:
                    pixels[int(color_data[0])] = color_data[1]
                pixels.show()
                
            onboard_pix.fill((0, 0, 0))
    
    
    ################################################################
    # Encoders
    ################################################################
    encoder_1_position = encoder_1.position
    encoder_2_position = encoder_2.position
    if encoder_1_last_position is None or encoder_1_position != encoder_1_last_position:
        # led.value = True
        encoder_1_position_change = encoder_1_position - encoder_1_last_position

        msgContructor2("Encoder1", "rotary encoder", not encoder_1_button.value, encoder_1_position_change)
        time.sleep(0.1)
        # led.value = False


    encoder_1_last_position = encoder_1_position

    if encoder_2_last_position is None or encoder_2_position != encoder_2_last_position:
        # led.value = True
        encoder_2_position_change = encoder_2_position -  encoder_2_last_position

        msgContructor2("Encoder2", "rotary encoder", not encoder_2_button.value, encoder_2_position_change)
        time.sleep(0.1)
        # led.value = False


    encoder_2_last_position = encoder_2_position

    # if not encoder_1_button.value and encoder_1_button_state is None:
    #     encoder_1_button_state = "pressed"
    #     print("Button pressed.")
    # if encoder_1_button.value and encoder_1_button_state == "pressed":
    #     print("Button released.")
    #     encoder_1_button_state = None
    
    ################################################################
    # Buttons
    ################################################################
    if MatrixEvent := keys.events.get():
        # this is the main 4x3 key grid.
        
        if MatrixEvent.pressed:
            # when the button is pressed, all I want it to do is put the time stamp in he held_keys list 
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
            msgContructor2(MatrixEvent, 'button')
            pixels[MatrixEvent.key_number] = (0, 0, 0)
            pixels.show()


    if ModeEvent := ModeButton.events.get():
        # this is the mode button
        if ModeEvent.pressed:
            pixels[12] = (255, 0, 0)
            pixels.show()
            held_keys[-1]  = ModeEvent.timestamp

        if ModeEvent.released:
            msgContructor2(ModeEvent, "mode")
            pixels[12] = (0, 0, 0)
            pixels.show()
