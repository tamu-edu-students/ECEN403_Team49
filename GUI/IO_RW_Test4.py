import pandas as pd #Pandas for database creation
import time
import random

from threading import Thread
import tkinter as tk
from tkinter import *
from tkinter import ttk

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.pyplot as plt
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

from MCP3008 import MCP3008
import time
import RPi.GPIO as GPIO

adc = MCP3008()

cV = 0
cI = 0
cP = 0
dV = 0
dI = 0
dP = 0

isFree = 0
isMode = 2

#~~~~~~~~~~~~~~~~~~~ PIN ASSIGNMENTS ~~~~~~~~~~~~~~~~~~~~~~#
charFET = 11
disFET = 13
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


def setup():
    print ("Setting up GPIO pins....")

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(charFET,GPIO.OUT) #Setup charge side PFET gpio
    GPIO.output(charFET, GPIO.LOW) #Initialize charge PFET to OFF
    GPIO.setup(disFET,GPIO.OUT) #Setup discharge side PFET gpio
    GPIO.output(disFET, GPIO.LOW) #Initialize discharge PFET to OFF

def getInput():

    global cV,cI,cP,dV,dI,dP

    while True:
        t = time.localtime()
        cV = (adc.read(channel=0)) * (5.21/1023.0)
        cI = (adc.read(channel=1)) * (5.21/1023.0)
        cP = cV * cI
        dV = (adc.read(channel=3)) * (5.21/1023.0)
        dI = (adc.read(channel=4)) * (5.21/1023.0)
        dP = dV * dI

        root.update()

def regen():
    count = 0
    global database
    global canvas1
    global line1
    global PowerText
    global ChargeText

    global cV,cI,cP,dV,dI,dP

    while True:
        time.sleep(0.05)
        count += 1

        if count % 20 == 0:

            database = database.shift(-1)
            database.loc[9] = [cV,cI,dV,dI]

            ax1.cla()
            ax1.plot(range(10),database['Value'],database['Current'])
            ax1.set_ylim(0,4)
            ax1.set_title("Charge Side Voltage")
            ax1.set_ylabel("Voltage [V]")
            canvas1.draw()

            ax2.cla()
            ax2.plot(range(10),database['Value'],database['Current'])
            ax2.set_ylim(0,4)
            ax2.set_title("Discharge Side Voltage")
            ax2.set_ylabel("Voltage [V]")
            canvas1.draw()

            PowerText.set(cP)
            ChargeText.set("24 %")

        if count == 200:

            #plt.figure(fig2)
            # plt.clf()
            # plt.scatter(range(11),database['Value'])
            count = 0



            
        
root = Tk()
root.title("MCU to Graph Test")

tabControl = ttk.Notebook(root)

tabDat = Frame(tabControl)
tabCtl = Frame(tabControl)

tabControl.add(tabDat, text='Data and Graphs')
tabControl.add(tabCtl, text='Control Systems')
tabControl.pack(expand=1, fill="both")

d = {'CV':[0,0,0,0,0,0,0,0,0,0],'CI':[0,0,0,0,0,0,0,0,0,0],
    'DV':[0,0,0,0,0,0,0,0,0,0],'DI':[0,0,0,0,0,0,0,0,0,0]}
database = pd.DataFrame(data= d)

fig1,ax1 = plt.subplots()
fig1.set_size_inches(5,4)
fig1.set_dpi(80)
ax1.plot(range(10),database['CV'],database['CI'])
ax1.autoscale(False)
ax1.set_title("Charge Side Voltage")
ax1.set_ylabel("Voltage [V]")

fig2,ax2 = plt.subplots()
fig2.set_size_inches(5,4)
fig2.set_dpi(80)
ax2.plot(range(10),database['DV'],database['DI'])
ax2.autoscale(False)
ax2.set_title("Discharge Side Voltage")
ax2.set_ylabel("Voltage [V]")

graphFrame = Frame(master=tabDat)
graphFrame.pack(side= LEFT)

canvas1 = FigureCanvasTkAgg(fig1,graphFrame)
canvas1.draw()
canvas1.get_tk_widget().pack(side= TOP)

canvas2 = FigureCanvasTkAgg(fig2,graphFrame)
canvas2.draw()
canvas2.get_tk_widget().pack(side= BOTTOM)

PowerText = StringVar(root,"0")
ChargeText = StringVar(root,"0")

#imgPanel = PhotoImage(file='panel.png',master=root)
#imgPanel = imgPanel.subsample(1,1)
#imgArrow = PhotoImage(file='arrow.png',master=root)
#imgArrow = imgArrow.subsample(20,20)
#imgBattery = PhotoImage(file='battery.png',master=root)
#imgBattery = imgBattery.subsample(3,3)

measureFrame = Frame(master= tabDat)
measureFrame.pack(side= RIGHT)

Label(measureFrame,font=(18), textvariable = PowerText,fg="black").grid(column=1,row=5)
Label(measureFrame,font=(18), textvariable = ChargeText,fg="black").grid(column=3,row=5)

Label(measureFrame,font=(18),text= "Charge-side Power [W]").grid(column=1,row=4)
Label(measureFrame,font=(18),text= "Battery Charge [%]").grid(column=3,row=4)

#Label(master= measureFrame,image=imgPanel).grid(column = 1, row = 3)
#Label(master= measureFrame,image=imgArrow).grid(column = 2, row = 3)
#Label(master= measureFrame,image=imgBattery).grid(column = 3, row = 3)


# ----------------- Control Tab ----------------
Label(tabCtl, text='Here we display our control functionality').grid(column=0, row=0, padx=10, pady=10)

## Include State Icons
# imgFixed = PhotoImage(file='panelFixed.png',master=tabCtl)
# imgFixed = imgFixed.subsample(2,2)
# imgFree = PhotoImage(file='panelFree.png',master=tabCtl)
# imgFree = imgFree.subsample(2,2)
# imageAngle = Label(master= tabCtl,image=imgFixed)
# imageAngle.grid(column = 2, row = 1)

# imgChar = PhotoImage(file='modeC.png',master=tabCtl)
# imgChar = imgChar.subsample(2,2)
# imgDis = PhotoImage(file='modeD.png',master=tabCtl)
# imgDis = imgDis.subsample(2,2)
# imageMode = Label(master= tabCtl,image=imgChar)
# imageMode.grid(column = 2, row = 2)

## Change axis state 
modeText1 = StringVar(tabCtl,"Press to initialize sysetm.")
Label(tabCtl, textvariable = modeText1,fg="black").grid(column=0,row=1,pady = 50)

def switchFree():
    global isFree
    global modeText1

    if isFree:
        modeText1.set("The system is in fixed-axis mode")
        #imageAngle.configure(image= imgFixed)
        isFree = False

    else:
        modeText1.set("The system is in free-axis mode")
        #imageAngle.configure(image= imgFree)
        isFree = True

Button(tabCtl, command=switchFree, text="Change Axis Mode").grid(column=1,row=1,pady = 50)

##Change charging state
modeText2 = StringVar(tabCtl,"Press button to initialize")
Label(tabCtl, textvariable = modeText2,fg="black").grid(column=0,row=2,pady = 50)

def switchMode():
    global isMode
    global modeText2

    if isMode == 2:
        GPIO.output(charFET,GPIO.HIGH) #Turn on charge-side FET
        modeText2.set("The system is being charged by the solar panel")
        isMode = 0

    elif isMode: #If sytem is in state 1 (discharging), change to state 0 (charging)
        GPIO.output(charFET,GPIO.HIGH) #Turn on charge-side FET
        GPIO.output(disFET,GPIO.LOW) #Turn off discharge-side FET
        modeText2.set("The system is being charged by the solar panel")
        #imageMode.configure(image= imgChar)
        isMode = 0

    else: #If sytem is in state 0 (charging), change to state 1 (discharging)
        GPIO.output(charFET,GPIO.LOW) #Turn off charge-side FET
        GPIO.output(disFET,GPIO.HIGH) #Turn on discharge-side FET
        modeText2.set("The system is discharging power to the load")
        #imageMode.configure(image= imgDis)
        isMode = 1

Button(tabCtl, command=switchMode, text="Change Charging Mode").grid(column=1,row=2,pady = 50)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ MAIN FUNCTION ~~~~~~~~~~~~~~~~~~~~~~~#

setup()

t1 = Thread(target = regen)
t2 = Thread(target = getInput)

t1.start()
t2.start()

root.mainloop()
