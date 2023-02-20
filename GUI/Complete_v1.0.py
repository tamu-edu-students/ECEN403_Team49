import pandas as pd #Pandas for database creation
import os

import tkinter as tk
from tkinter import *
from tkinter import ttk

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.pyplot as plt
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

#
# ~~~~~~~~~~~~~~~~~ INTERNAL VARIABLES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
isFree = 0
isMode = 0

#
# ~~~~~~~~~~~~~~~~~ DATBASE READER ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#

database = pd.read_csv("dummy1.csv")

#
# ~~~~~~~~~~~~~~~~~ GRAPH GENERATOR ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#

fig1 = plt.figure()
t = database['TIME']
y2A = database['V(Charge)']
y1A = database['V(Discharge)']
fig1A = fig1.add_subplot(111)
plt.bar(t,y1A,label='charging')
plt.bar(t,y2A,label='discharging')
fig1A.set_title("Voltage 'V' Measurements")
fig1A.set_xlabel("Time [s]")
fig1A.set_ylabel("Voltage [V]")
fig1A.legend()

fig2 = plt.figure()
y1B = database['I(Charge)']
y2B = database['I(Discharge)']
fig2A = fig2.add_subplot(111)
plt.bar(t,y1B,label='charging')
plt.bar(t,y2B,label='discharging')
fig2A.set_title("Current 'I' Measurements")
fig2A.set_xlabel("Time [s]")
fig2A.set_ylabel("Current [mA]")
fig2A.legend()

fig3 = plt.figure(figsize=(3,2),dpi=100)
y1C = database['P(Charge)']
y2C = database['P(Discharge)']
plt.bar(t,y1C)
plt.bar(t,y2C)


#
# ~~~~~~~~~~~~~~~~~ GUI BUILDER ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#

# Create parent window
root = Tk()
root.title("Solar Panel Charging System")
#root.attributes('-fullscreen',True)

tabControl = ttk.Notebook(root)

tabDat = Frame(tabControl)
tabAni = Frame(tabControl)
tabCtl = Frame(tabControl)

tabControl.add(tabDat, text='Data and Graphs')
tabControl.add(tabAni, text='System Animation')
tabControl.add(tabCtl, text='Control Systems')

tabControl.pack(expand=1, fill="both")

# ----------------- Graphs Tab ----------------
ttk.Label(tabDat, text='Here we display our infographics').grid(column=0, row=0, padx=10, pady=10)

canvas1 = FigureCanvasTkAgg(fig1,tabDat)
canvas1.draw()
canvas1.get_tk_widget().grid(column=0,row=1,padx=20,pady=20)

canvas2 = FigureCanvasTkAgg(fig2,tabDat)
canvas2.draw()
canvas2.get_tk_widget().grid(column=1,row=1,padx=20,pady=20)

canvas3 = FigureCanvasTkAgg(fig3,tabDat)
canvas3.draw()
canvas3.get_tk_widget().grid(column=0,row=2,padx=20,pady=20)

ttk.Label(tabDat, text= "Panel-side voltage reading: ").grid(column = 0, row = 3, padx = 10, pady=10)

# ----------------- Animation Tab ----------------
ttk.Label(tabAni, text='Here we display our system animation').grid(column=0, row=0, padx=10, pady=10)

imageA = tk.PhotoImage(file='..\\pic1.png')
ttk.Label(tabAni, image= imageA).grid(column=1,row=1)

# ----------------- Graphs Tab ----------------
Label(tabCtl, text='Here we display our control functionality').grid(column=0, row=0, padx=10, pady=10)

## Change axis state 
modeText1 = StringVar(tabCtl,"The system is in fixed-axis mode")
Label(tabCtl, textvariable = modeText1,fg="black").grid(column=0,row=1)

def switchFree():
    global isFree
    global modeText1

    if isFree:
        modeText1.set("The system is in fixed-axis mode")
        isFree = False

    else:
        modeText1.set("The system is in free-axis mode")
        isFree = True

Button(tabCtl, command=switchFree, text="Change Axis Mode").grid(column=1,row=1)

##Change charging state
modeText2 = StringVar(tabCtl,"The system is being charged by the solar panel")
Label(tabCtl, textvariable = modeText2,fg="black").grid(column=0,row=2,padx=10)

def switchMode():
    global isMode
    global modeText2

    if isMode:
        modeText2.set("The system is being charged by the solar panel")
        isMode = False

    else:
        modeText2.set("The system discharging power to the load")
        isMode = True

Button(tabCtl, command=switchMode, text="Change Charging Mode").grid(column=1,row=2)


root.mainloop()
