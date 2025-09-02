import os
import sys
from tkinter import *
from tkinter.ttk import *
import time

# I didn't save the finished version. TODO: See if I can do it again...

# ---------------------------- CONSTANTS ------------------------------- #
CREAM = "#FFF8E8"
BEIGE = "#F7EED3"
SAGE = "#AAB396"
BROWN = "#674636"
FONT_NAME = "Courier"

# ----------------------------  FUNCTIONS WILL GO HERE ------------------------------- #

# ----------------------------  UI SETUP ------------------------------- #

# Create TK window, define style & size:
window = Tk()

style = Style()
style.configure("TLabel", foreground=BROWN, background=BEIGE)

window.title("The most dangerous writing app.")
window.config(padx=100, pady=60, bg=BEIGE)
window.geometry('900x500')

# Text labels:
title_label = Label(text="Welcome to the most dangerous writing app.", style="TLabel", font=(FONT_NAME, 20, "bold"))
title_label.grid(column=1, columnspan=2, row=0)

text_label1 = Label(text="Don't stop writing, or all your progress will be lost.", style="TLabel", font=(FONT_NAME, 16))
text_label1.grid(column=1, columnspan=2, row=1, pady=20)

# Define buttons style:
button_style = Style().configure("TButton", padding=10, relief="flat", background="#ccc", foreground=BROWN)

# Buttons:
generate_prompt_button = Button(text="Generate prompt", command="#", style="TButton")
generate_prompt_button.grid(column=1, row=2, pady=20)
start_now = Button(text="Start writing w/o prompt", command="#", style="TButton")
start_now.grid(column=2, row=2, pady=20)

window.mainloop()
