"""
Listens to the REPL port, without using the usb_cdc module.
Receives color information and displays it on the NEOPIXEL.
Receives blink command and blinks once.
Sends button release and encoder position change.

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

import asyncio          #https://github.com/adafruit/Adafruit_CircuitPython_asyncio/tree/main
from rainbowio import colorwheel
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


# vales for encoder_1_button.value is inverted. its False when pressed.
encoder_1_button = digitalio.DigitalInOut(board.D8)
encoder_1_button.direction = digitalio.Direction.INPUT
encoder_1_button.pull = digitalio.Pull.UP
# encoder_1_button_state = None
#encoder_1 = rotaryio.IncrementalEncoder(board.D4, board.D5)
encoder_1 = rotaryio.IncrementalEncoder(board.D5, board.D4)
encoder_1_last_position = 0


encoder_2_button = digitalio.DigitalInOut(board.D9)
encoder_2_button.direction = digitalio.Direction.INPUT
encoder_2_button.pull = digitalio.Pull.UP
# encoder_2_button_state = None
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

# held_keys = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


active_btns = {}
layer_delay = 0.250 # in seconds
btn_pressed_color = (0, 255, 0)  
btn_active_layer_color = (255, 0, 0)   


def msgContructor4(msg):
    data_out = {}
    # print(msg)
    # all keys with a layer "atribute"
    layers = [key for key, values in active_btns.items() if values['layer']]
    # sorts the list
    layers = sorted(layers, key=lambda x: (isinstance(x, (int, float)), x))

    # checks if 21 and 22 are in the list, if they are, remove it
    if 21 in layers:
        layers.remove(21)
    if 22 in layers:
        layers.remove(22)
    
    # converts it all to strings
    layers = list(map(str, layers))
    
    
    data_out = msg
    if len(layers) !=0:
        data_out["Layers"] = layers 
    
    # message is complete.
    print(json.dumps(data_out))
    
    pixels[14] = (0, 255, 0)
    pixels.show()
    time.sleep(0.01)
    pixels[14] = (0, 0, 0)
    pixels.show()
    
    
def encoder_pos_change_to_msg(encoder_pos_change, btn):
    if encoder_pos_change < 0:
        encoder_val = "CCW"
    else:
        encoder_val = "CW"
    if btn:
        encoder_val+="B"
        
    return encoder_val


"""
# async def layer_color_changer():
#     # await asyncio.sleep(0.100)
#     #await asyncio.sleep(0.130)
#     wait = 0.100
#     await asyncio.sleep(wait)
#     #time.sleep(wait)
#     #0.250
#     #print(f"have sleeped for {wait} secs")
#     for index, key in enumerate(held_keys):
#         #print(key)
#         if key != 0:  # if any var is not 0

#             #if there is a button  that is being held
#             diff = ((supervisor.ticks_ms() - key)/1000)#-wait
#             # print(diff)
#             # takes the current time - var div by 1000
#             # if diff > 0.100: # if the diff is greater then 0.1s, ie been pressed for more then 0.1s 
#             if diff > wait: # if the diff is greater then 0.1s, ie been pressed for more then 0.1s 
#                 # print(f"diff is greater then {wait} for {key}, changing color {held_keys.index(key)}, {index}, {diff}")
#                 pixels[index] = (255,0,0)
#                 pixels.show()        
            
              
#     # for i in held_keys: #loops through all the items in held_keys list
#     #     print(i)
#     #     if i != 0:  # if any var is not 0
#     #         #if there is a button  that is being held
#     #         diff = (supervisor.ticks_ms() - i)/1000
#     #         # takes the current time - var div by 1000
#     #         if diff > 0.100: # if the diff is greater then 0.1s, ie been pressed for more then 0.1s 
#     #             #changes coolor to yellow
#     #             # pixels[held_keys.index(i)] = (255,255,0)
#     #             print(f"diff is greater then 0.100 for {i}, changing color {held_keys.index(i)}")
#     #             pixels[held_keys.index(i)] = (255,0,0)
#     #             pixels.show()

# async def layer_color_changer2(min_diff = 0.100, key = None):
#     if key is not None:
#         timestamp  = held_keys_dict[key]
#         diff = ((supervisor.ticks_ms() - timestamp)/1000)
#         # takes the current time - var div by 1000
#         if diff > min_diff: # if the diff is greater then 0.1s, ie been pressed for more then 0.1s 
#             print(f"greater then2, {diff}")
#             print(supervisor.ticks_ms())
#             if key =="Mode":
#                 pixels[12] = (255,0,0)
#             else:
#                 pixels[key] = (255,0,0)
#             # pixels[key] = (255,0,0)
#             pixels.show()  
#             time.sleep(0.05)
#         return
    
    
#     # await asyncio.sleep(min_diff)
    
#     # await asyncio.sleep(0.100)
#     for key, timestamp in held_keys_dict.items():
#         print(key, timestamp) 
    
#         diff = ((supervisor.ticks_ms() - timestamp)/1000)
#         # takes the current time - var div by 1000
#         if diff > min_diff: # if the diff is greater then 0.1s, ie been pressed for more then 0.1s 
#             print(f"greater then1, {diff}, ")
#             print(supervisor.ticks_ms())
            
#             if key =="Mode":
#                 pixels[12] = (255,0,0)
#             else:
#                 pixels[key] = (255,0,0)
#             pixels.show()       

    
#     if diff < (min_diff+0.010):
#         print("sda")
#         await asyncio.sleep(min_diff)
#         asyncio.run(layer_color_changer2(key=key))
"""        


################################################################
# loop-y-loop
################################################################

def main():
    encoder_1_last_position = 0
    encoder_2_last_position = 0 
    encoder_1_button_last_pos = 1
    encoder_2_button_last_pos = 1
    
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
        # BTN checks
        ################################################################
        if len(active_btns):
            for key, values in active_btns.items():
                if values['layer']:
                    continue
                time_diff = (supervisor.ticks_ms() - values['time'])/1000
                if time_diff > layer_delay:
                    pxl = values['led']['num']
                        
                    pixels[pxl] = btn_active_layer_color
                    pixels.show()
                    active_btns[key]['led']['color'] = btn_active_layer_color                 
                    active_btns[key]['layer'] = True

                
        ################################################################
        # Encoders
        ################################################################
        encoder_1_position = encoder_1.position
        encoder_2_position = encoder_2.position
        if encoder_1_last_position is None or encoder_1_position != encoder_1_last_position:
            
            encoder_1_position_change = encoder_1_position - encoder_1_last_position
            value_msg = encoder_pos_change_to_msg(encoder_1_position_change, not encoder_1_button.value)
            msg = {'Encoder': [{'Id': 1, 'Value': value_msg}]}
            
            msgContructor4(msg)
        encoder_1_last_position = encoder_1_position

        if encoder_2_last_position is None or encoder_2_position != encoder_2_last_position:

            encoder_2_position_change = encoder_2_position -  encoder_2_last_position
            value_msg = encoder_pos_change_to_msg(encoder_2_position_change, not encoder_2_button.value)
            msg = {'Encoder': [{'Id': 2, 'Value': value_msg}]}
            
            msgContructor4(msg)
        encoder_2_last_position = encoder_2_position

        ################################################################
        # Encoders Buttons
        ################################################################
        if encoder_1_button.value != encoder_1_button_last_pos:
            # btn is released
            if encoder_1_button.value:
                if 21 in active_btns.keys():
                    if not active_btns[21]['layer']:
                        msg = {'Encoder': [{'Id': 1, 'Value': 'B'}]}
                        msgContructor4(msg)
                        
                    pxl = active_btns[21]['led']['num']
                    pixels[pxl] = (0, 0, 0)
                    pixels.show()
                    active_btns.pop(21)        
                
            # button is pressed
            else:
                active_btns[21] = {'status':True, 'time':supervisor.ticks_ms(), 'led':{'num':13,'color':btn_pressed_color}, 'layer': False}
                
                pixels[13] = btn_pressed_color        #turns it green
                pixels.show()
        encoder_1_button_last_pos = encoder_1_button.value
        
        if encoder_2_button.value != encoder_2_button_last_pos:
            # btn is released
            if encoder_2_button.value:
                if 22 in active_btns.keys():
                    if not active_btns[22]['layer']:
                        msg = {'Encoder': [{'Id': 2, 'Value': 'B'}]}
                        msgContructor4(msg)
                        
                    pxl = active_btns[22]['led']['num']
                    pixels[pxl] = (0, 0, 0)
                    pixels.show()
                    active_btns.pop(22)
                
            # button is pressed
            else:
                active_btns[22] = {'status':True, 'time':supervisor.ticks_ms(), 'led':{'num':13,'color':btn_pressed_color}, 'layer': False}
                
                pixels[13] = btn_pressed_color        #turns it green
                pixels.show()
        encoder_2_button_last_pos = encoder_2_button.value
        
        ################################################################
        # Buttons
        ################################################################
        if MatrixEvent := keys.events.get():
            # this is the main 4x3 key grid.
            
            if MatrixEvent.pressed:
                # when the button is pressed, all I want it to do is put the time stamp in he held_keys list 
                active_btns[MatrixEvent.key_number] = {'status':True, 'time':MatrixEvent.timestamp, 'led':{'num':MatrixEvent.key_number,'color':btn_pressed_color}, 'layer': False}
                pixels[MatrixEvent.key_number] = btn_pressed_color        #turns it green
                pixels.show()
                
            if MatrixEvent.released:
                if not active_btns[MatrixEvent.key_number]['layer']:
                    msgContructor4({'ButtonId': MatrixEvent.key_number + 1})
              
                pixels[MatrixEvent.key_number] = (0, 0, 0)
                pixels.show()
                active_btns.pop(MatrixEvent.key_number)
                
                
        if ModeEvent := ModeButton.events.get():
            # this is the mode button
            if ModeEvent.pressed:
                active_btns["Mode"] = {'status':True, 'time':ModeEvent.timestamp, 'led':{'num':12,'color':btn_pressed_color}, 'layer': False}
                pixels[12] = btn_pressed_color        #turns it green
                pixels.show()
            
                # asyncio.run(layer_color_changer2())
                
            if ModeEvent.released:
                if not active_btns["Mode"]['layer']:
                    msgContructor4({'ButtonId': 'Mode'})
            
                pixels[12] = (0, 0, 0)
                pixels.show()
                active_btns.pop("Mode")
       

def startup():
    pixels.fill((0,255,0))
    pixels.show()
    
    time.sleep(0.25)
    
    pixels.fill((255,0,255))
    pixels.show()
    
    time.sleep(0.25)
    
    pixels.fill((0,0,0))
    pixels.show()
    time.sleep(0.25)
    
    pixels.fill((0,255,0))
    pixels.show()
    
    time.sleep(0.25)
    
    pixels.fill((0,0,0))
    pixels.show()
    
    time.sleep(0.25)
    pixels.fill((255,0,255))
    pixels.show()
    
    time.sleep(0.25)
    pixels.fill((0,0,0))
    pixels.show()
    
if __name__ == "__main__":
    startup()
    
    main()