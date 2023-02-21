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
    global line1
    global PowerText
    global ChargeText

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
            database.loc[9] = [cV]

            ax1.cla()
            ax1.plot(range(10),database['Value'])
            ax1.set_ylim(0,4)
            ax1.set_title("Charge Side Voltage")
            ax1.set_ylabel("Voltage [V]")

            canvas1.draw()

            PowerText.set(cP)
            ChargeText.set("24 %")

        if count == 200:

            #plt.figure(fig2)
            # plt.clf()
            # plt.scatter(range(11),database['Value'])
            count = 0
        
        root.update()
            
        
root = Tk()
root.title("MCU to Graph Test")

#tk.Label(master= root, text= 'Below should be the updating graph:').pack()

d = {'Value':[0,0,0,0,0,0,0,0,0,0]}
database = pd.DataFrame(data= d)

fig1,ax1 = plt.subplots()
fig1.set_size_inches(5,4)
fig1.set_dpi(120)
ax1.plot(range(10),database['Value'])
ax1.autoscale(False)
ax1.set_title("Charge Side Voltage")
ax1.set_ylabel("Voltage [V]")

#plt2 = fig.add_subplot(1,1,2)

#plt2.scatter(range(50),range(50))

graphFrame = Frame(master=root)
graphFrame.pack(side= TOP)


canvas1 = FigureCanvasTkAgg(fig1,graphFrame)
canvas1.draw()
canvas1.get_tk_widget().pack(side= TOP)

PowerText = StringVar(root,"0")
ChargeText = StringVar(root,"0")

imgPanel = PhotoImage(file='panel.png',master=root)
imgPanel = imgPanel.subsample(1,1)
imgArrow = PhotoImage(file='arrow.png',master=root)
imgArrow = imgArrow.subsample(20,20)
imgBattery = PhotoImage(file='battery.png',master=root)
imgBattery = imgBattery.subsample(3,3)

measureFrame = Frame(master= root)
measureFrame.pack(side= BOTTOM)

Label(measureFrame,font=(18), textvariable = PowerText,fg="black").grid(column=1,row=5)
Label(measureFrame,font=(18), textvariable = ChargeText,fg="black").grid(column=3,row=5)

Label(measureFrame,font=(18),text= "Charge-side Power [W]").grid(column=1,row=4)
Label(measureFrame,font=(18),text= "Battery Charge [%]").grid(column=3,row=4)

Label(master= measureFrame,image=imgPanel).grid(column = 1, row = 3)
Label(master= measureFrame,image=imgArrow).grid(column = 2, row = 3)
Label(master= measureFrame,image=imgBattery).grid(column = 3, row = 3)

##Enter LOOP
root.after(0,regen)

root.mainloop()
