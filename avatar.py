from turtle import *
import tkinter as tk

speed(0)
bgcolor("black")
color("orange")
hideturtle()
n = 1
p = True
try:
    while True:
        circle(n)
        if p:
            n = n - 1
        else:
            n = n + 1
        if n == 0 or n == 60:
            p = not p
        left(1)
        forward(3)
except (Terminator, tk.TclError):
    # Gracefully catch shutdown when window is closed
    pass
