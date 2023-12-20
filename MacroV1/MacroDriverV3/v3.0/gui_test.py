import tkinter as tk
import tkinter.font as tkfont
import itertools

mode = 1

# Define a function to print the name of the button that was clicked
def print_button_name(button_name):
    global mode
    if button_name == 'Mode':
        if mode < 4:
            mode += 1
        else:
            mode = 1

    if button_name != 'Mode' and 10 <= button_name <= 12:
        button_names = {'10': '0', 
            '11': 'A', 
            '12': 'B'}
        button_name = button_names[str(button_name)]

    print(f"Button {button_name} was clicked.")

    if button_name != 'Mode':
        button_str_to_send = f'{button_name} {mode}'
        #print(button_tsr_to_send)
        try:
            pass
            #Button_handler(button_str_to_send)
        except Exception as e:
            print(e)
        #devmacro.Button_handler(button_str_to_send)

    #print(button_names[button])

def main():
    root = tk.Tk()
    root.geometry("420x420")
    root.title("macro_info_gui_test")

    for i, j in itertools.product(range(3), range(5)):
        if i < 2 and j == 0:
            continue

        number = (4*i) +j  

        button = tk.Button(root, text=f"Button {number}", width = 10, height = 4,  command=lambda name=number: print_button_name(name))

        if i == 2 and j == 0 :
            button_name = "Mode"

            button = tk.Button(root, text= button_name, width = 10, height = 4,  command=lambda name=button_name: print_button_name(name))
        
        button.grid(row=i, column=j)

    import tkinter.font as tkfont
    font = tkfont.nametofont("TkDefaultFont")
    my_str="Arduino"

    height=font.measure(my_str)+10
    width=font.metrics()['linespace']

    canvas = tk.Canvas(root, height=height, width=width)
    canvas.create_text((0,6), angle=-90, anchor="sw", text=my_str, fill='SystemButtonText', font=font)
    canvas.grid(row=0, column=0, rowspan=2)

    """
            Column0     Column1     Column2     Column3     Column4
    Row0    Arduino1    Button1     Button2     Button3     Button4

    Row1    Arduino2    Button5     Button6     Button7     Button8

    Row2    Mode        Button9     Button10    Button11    Button12
    """

    #https://www.youtube.com/watch?v=XKHEtdqhLK8
    root.mainloop()




if __name__ == "__main__":
    mode = 1

    main()