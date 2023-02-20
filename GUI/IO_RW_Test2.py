import pandas as pd #Pandas for database creation
import os
import time
import random
import numpy

import tkinter as tk
from tkinter import *
from tkinter import ttk

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.pyplot as plt
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

from MCP3008 import MCP3008
import time
import RPi.GPIO as GPIO

adc = MCP3008()

def regen():
    count = 0
    global database
    global canvas1
    global plt1
    global plt2
    global plt

    while True:
        time.sleep(0.05)
        root.update()
        count += 1

        t = time.localtime()
        cV = (adc.read(channel=0)) * (5.21/1023.0)
        cI = (adc.read(channel=1)) * (5.21/1023.0)
        cP = cV * cI
        dV = (adc.read(channel=2)) * (5.21/1023.0)
        dI = (adc.read(channel=3)) * (5.21/1023.0)
        dP = dV * dI

        if count % 20 == 0:
            
            database = database.shift(-1)
            database.loc[-1] = [t,cV,cI,cP,dV,dI,dP]

            plt1.cla()
            plt1.set_ylim(0,4)
            plt1.scatter(range(11),database['Power (C)'])

            canvas1.draw()

        if count == 200:

            plt2.cla()
            plt2.scatter(database['Time'],database['Power (C)'])
            
            canvas1.draw()
            count = 0
        
        root.update()
            
        
root = Tk()
root.title("MCU to Graph Test")

tk.Label(master= root, text= 'Below should be the updating graph:').pack(side='top')

d = {'Value':[0,0,0,0,0,0,0,0,0,0]}
database = pd.DataFrame(data= d)

fig = plt.figure()
plt1 = fig.add_subplot(1,1,1)
plt1.scatter(range(10),database['Value'])
plt1.autoscale(False)

#plt2 = fig.add_subplot(2,1,2)
#plt2.scatter(range(50),range(50))

canvas1 = FigureCanvasTkAgg(fig,root)
canvas1.draw()
canvas1.get_tk_widget().pack(side='top')

##Enter LOOP
root.after(0,regen)

root.mainloop()
