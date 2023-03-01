from tkinter import *
mode = 0


window = Tk()
window.geometry("420x420")
window.title("macro_info_gui_test")
window.config(background='black')

modeButton = Button(window, text="Mode", width=10, height=4).grid(row=2, column=0)

Button1= Button(window, text='Button 1', width=10, height=4).grid(row=0, column=1)
Button2= Button(window, text='Button 2', width=10, height=4).grid(row=0, column=2)
Button3= Button(window, text='Button 3', width=10, height=4).grid(row=0, column=3)
Button4= Button(window, text='Button 4', width=10, height=4).grid(row=0, column=4)

Button5= Button(window, text='Button 5', width=10, height=4).grid(row=1, column=1)
Button6= Button(window, text='Button 6', width=10, height=4).grid(row=1, column=2)
Button7= Button(window, text='Button 7', width=10, height=4).grid(row=1, column=3)
Button8= Button(window, text='Button 8', width=10, height=4).grid(row=1, column=4)

Button9= Button(window, text='Button 9', width=10, height=4).grid(row=2, column=1)
Button10= Button(window, text='Button 10', width=10, height=4).grid(row=2, column=2)
Button11= Button(window, text='Button 11', width=10, height=4).grid(row=2, column=3)
Button12= Button(window, text='Button 12', width=10, height=4).grid(row=2, column=4)

"""
        Column0     Column1     Column2     Column3     Column4
Row0    Arduino1    Button1     Button2     Button3     Button4

Row1    Arduino2    Button5     Button6     Button7     Button8

Row2    Mode        Button9     Button10    Button11    Button12
"""


#https://www.youtube.com/watch?v=XKHEtdqhLK8
window.mainloop()