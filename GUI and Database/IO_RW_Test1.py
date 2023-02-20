import pandas as pd #Pandas for database creation
import os
import time

import tkinter as tk
from tkinter import *
from tkinter import ttk

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.pyplot as plt
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

#from MCP3008 import MCP3008
#import time
#import RPi.GPIO as GPIO

def update_data():
    # TO DO #
    root.after(10000,update_data)

root = Tk()
root.title("MCU to Graph Test")

tk.Label(master= root, text= 'Below should be the updating graph:').pack(side='top')

database = pd.read_csv('dummy3.csv') 

fig1 = plt.figure()
plt.scatter(database['Time'],database['Value'])

canvas1 = FigureCanvasTkAgg(fig1,root)
canvas1.draw()
canvas1.pack(side='top')

root.mainloop()
