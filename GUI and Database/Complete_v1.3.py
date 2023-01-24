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

#
# ~~~~~~~~~~~~~~~~~ INTERNAL VARIABLES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
photos = []
isFree = 0
isMode = 0
chargeI = 0.002
chargeV = 0.0001
dischargeI = 0.32
dischargeV = 3.5

#
# ~~~~~~~~~~~~~~~~~ DATBASE READER ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#

database = pd.read_csv("dummy1.csv") #Read data from database (CSV)

fig1 = plt.figure()
t = database['TIME']                    # These lines all create
y2A = database['V(Charge)']             # series of data from columns
y1A = database['V(Discharge)']          # found in CSV file
plt.scatter(t,y1A,label='charging')
plt.scatter(t,y2A,label='discharging')
plt.autoscale(True, 'both', True)
plt.title("Voltage 'V' Measurements",fontsize=9)
plt.xlabel("Time [s]",fontsize=8)
plt.ylabel("Voltage [V]",fontsize=8)
plt.legend()

fig2 = plt.figure()
y1B = database['I(Charge)']
y2B = database['I(Discharge)']
plt.scatter(t,y1B,label='charging')
plt.scatter(t,y2B,label='discharging')
plt.autoscale(True, 'both', True)
plt.title("Current 'I' Measurements",fontsize=9)
plt.xlabel("Time [s]",fontsize=8)
plt.ylabel("Current [mA]",fontsize=8)
plt.legend()

fig3 = plt.figure()
y1C = database['P(Charge)']
y2C = database['P(Discharge)']
plt.scatter(t,y1C,label='charging')
plt.scatter(t,y2C,label='discharging')
#plt.autoscale(True, 'both', True)
plt.title("Power 'P' Measurements",fontsize=9)
plt.xlabel("Time [s]",fontsize=8)
plt.ylabel("Power [W]",fontsize=8)
plt.legend()

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
ttk.Label(tabDat, text='Here we display our infographics  #NOTE: These graphs are calulated using dummy data').grid(column=0, row=0, padx=0, pady=10,sticky="W")

canvas1 = FigureCanvasTkAgg(fig1,tabDat)
canvas1.draw()
canvas1.get_tk_widget().grid(column=0,row=1,padx=20,pady=10)
canvas1.get_tk_widget().config(width=450,height=350)

canvas2 = FigureCanvasTkAgg(fig2,tabDat)
canvas2.draw()
canvas2.get_tk_widget().grid(column=1,row=1,padx=20,pady=10)
canvas2.get_tk_widget().config(width=450,height=350)

canvas3 = FigureCanvasTkAgg(fig3,tabDat)
canvas3.draw()
canvas3.get_tk_widget().grid(column=2,row=1,padx=20,pady=10)
canvas3.get_tk_widget().config(width=450,height=350)

ttk.Label(tabDat, text= "Panel-side voltage reading:\t" + str(chargeV) + "  V").grid(column = 0, row = 3, padx = 10, pady=10,sticky="w")
ttk.Label(tabDat, text= "Panel-side current reading:\t" + str(chargeI) + "  A").grid(column = 0, row = 4, padx = 10, pady=10,sticky="w")


ttk.Label(tabDat, text= "Load-side voltage reading:\t" + str(dischargeV) + "  V").grid(column = 1, row = 3, padx = 30, pady=10,sticky="w")
ttk.Label(tabDat, text= "Load-side current reading:\t" + str(dischargeI) + "  A").grid(column = 1, row = 4, padx = 30, pady=10,sticky="w")
# ----------------- Animation Tab ----------------
ttk.Label(tabAni, text='Here we display our system animation').grid(column=0, row=0, padx=0, pady=10)

# Intialize Frames of Animation as PhotoImages
framesChar = [PhotoImage(master=tabAni,file='chargeAnim/ani_charge%i.png' %(i)) for i in range(6)]
framesDis = [PhotoImage(master=tabAni,file='dischargeAnim/ani_discharge%i.png' %(i)) for i in range(6)]

#initialize animation photo in cneter of frame
animation = Label(tabAni,image = None)
animation.grid(column=1,row=2)

#Cycle through the individual frames of the animation
def playChar(i):
    global check                            # ID given to task; Used
    frame = framesChar[i]                   # to reset task when needed
    i += 1
    if i == 6:
        i = 0
    animation.configure(image=frame)        #push next frame
    check = root.after(1000,playChar,i)     #iterate after ~1 sec

#Restart Animation frames
def resetChar():
    try:
        root.after_cancel(check)            # Break/reset prior animation loop
    except:
        pass
    animation.configure(image= framesChar[0])
    playChar(0)

# Cycle through the individual frames of the animation
def playDis(j):
    global check
    frame = framesDis[j]
    j += 1
    if j == 6:
        j = 0
    animation.configure(image=frame)
    check = root.after(1000,playDis,j) 

#Restart Animation frames
def resetDis():
    try:
        root.after_cancel(check)
    except:
        pass 
    animation.configure(image= framesDis[0])
    playDis(0)

# Create buttons to reset animations when pressed
Button(tabAni, text="Restart Charge Animation",command=resetChar).grid(column=0,row=1,padx=30)
Button(tabAni, text="Restart Discharge Animation",command=resetDis).grid(column=1,row=1)

# ----------------- Control Tab ----------------
Label(tabCtl, text='Here we display our control functionality').grid(column=0, row=0, padx=10, pady=10)
#Label(tabCtl, text='Here we can display a little graphic to show operating mode').grid(column=0, row=3, padx=10, pady=10)

## Include State Icons
imgFixed = PhotoImage(file='panelFixed.png',master=tabCtl)
imgFixed = imgFixed.subsample(2,2)
imgFree = PhotoImage(file='panelFree.png',master=tabCtl)
imgFree = imgFree.subsample(2,2)
imageAngle = Label(master= tabCtl,image=imgFixed)
imageAngle.grid(column = 2, row = 1)

## Change axis state 
modeText1 = StringVar(tabCtl,"The system is in fixed-axis mode")
Label(tabCtl, textvariable = modeText1,fg="black").grid(column=0,row=1,pady = 50)

def switchFree():
    global isFree
    global modeText1

    if isFree:
        modeText1.set("The system is in fixed-axis mode")
        imageAngle.configure(image= imgFixed)
        isFree = False

    else:
        modeText1.set("The system is in free-axis mode")
        imageAngle.configure(image= imgFree)
        isFree = True

Button(tabCtl, command=switchFree, text="Change Axis Mode").grid(column=1,row=1,pady = 50)

##Change charging state
modeText2 = StringVar(tabCtl,"The system is being charged by the solar panel")
Label(tabCtl, textvariable = modeText2,fg="black").grid(column=0,row=2,pady = 50)

def switchMode():
    global isMode
    global modeText2

    if isMode:
        modeText2.set("The system is being charged by the solar panel")
        isMode = False

    else:
        modeText2.set("The system discharging power to the load")
        isMode = True

Button(tabCtl, command=switchMode, text="Change Charging Mode").grid(column=1,row=2,pady = 50)

root.mainloop()
