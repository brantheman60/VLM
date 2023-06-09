from tkinter import *
import tkinter as tk
import time

def foo(event):
    print(event.x, event.y)
    button.forget()

window = Tk()
button = Button(window, text='foo')
# button.bind('<Button-1>', foo)
# button.bind('<Button-3>', lambda e: window.quit())
button.bind('<Button>', foo)
button.pack()
window.mainloop()