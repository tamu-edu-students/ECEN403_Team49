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

        cV = random.randint(0,2)
        cI = random.randint(0,2)
        cP = cV * cI
        dV = random.randint(0,2)
        dI = random.randint(0,2)
        dP = dV * dI
        root.update()

def regen():
    count = 0
    global database
    global canvas1
    global line1
    global DischargeText
    global ChargeText

    global cV,cI,cP,dV,dI,dP

    while True:
        time.sleep(0.05)
        root.update()
        count += 1
        getInput

        if count % 10 == 0:
            t = time.localtime()
            cV = (adc.read(channel=0)) * (5.21/1023.0)
            cI = (adc.read(channel=1)) * (5.21/1023.0)
            cP = cV * cI
            dV = (adc.read(channel=3)) * (5.21/1023.0)
            dI = (adc.read(channel=4)) * (5.21/1023.0)
            dP = dV * dI

            ChargeText = "CV: " + str(cV) + "\t CI: " + str(cI) + "\t CP: " + str(cP)
            DischargeText = "CV: " + str(cV) + "\t CI: " + str(cI) + "\t CP: " + str(cP)

            database = database.shift(-1)
            database.loc[9] = [cV,cI,dV,dI]

            ax1a.cla()
            ax1a.plot(range(10),database['CV'])
            ax1a.set_ylim(0,4)
            ax1a.set_title("Charge Side Voltage")
            ax1a.set_ylabel("Voltage [V]")
            ax1b.cla()
            ax1b.plot(range(10),database['CI'])
            ax1b.set_title("Charge Side Current")
            ax1b.set_ylabel("Current [mA]")
            canvas1.draw()

            ax2a.cla()
            ax2a.plot(range(10),database['DV'])
            ax2a.set_ylim(0,4)
            ax2a.set_title("Discharge Side Voltage")
            ax2a.set_ylabel("Voltage [V]")
            ax2b.cla()
            ax2b.plot(range(10),database['DI'])
            ax2b.set_title("Discharge Side Current")
            ax2b.set_ylabel("Current [mA]")
            canvas2.draw()



        if count == 200:

            #plt.figure(fig2)
            # plt.clf()
            # plt.scatter(range(11),database['Value'])
            count = 0
        
        root.update()
           
        
root = Tk()
root.title("MCU to Graph Test")

tabControl = ttk.Notebook(root)

tabCtl = Frame(tabControl)
tabDat = Frame(tabControl)

tabControl.add(tabDat, text='Control Systems')
tabControl.pack(expand=1, fill="both")

tabControl.add(tabCtl, text='Control Systems')
tabControl.pack(expand=1, fill="both")

d = {'CV':[0,0,0,0,0,0,0,0,0,0],'CI':[0,0,0,0,0,0,0,0,0,0],
    'DV':[0,0,0,0,0,0,0,0,0,0],'DI':[0,0,0,0,0,0,0,0,0,0]}
database = pd.DataFrame(data= d)

fig1,(ax1a,ax1b) = plt.subplots(2,1)
fig1.set_size_inches(6,6)
fig1.set_dpi(80)
ax1a.plot(range(10),database['CV'])
ax1a.set_title("Charge Side Voltage")
ax1a.set_ylabel("Voltage [V]")
ax1b.plot(range(10),database['CI'])
ax1b.set_title("Charge Side Current")
ax1b.set_ylabel("Current [mA]")


fig2,(ax2a,ax2b) = plt.subplots(2,1)
fig2.set_size_inches(6,6)
fig2.set_dpi(80)
ax2a.plot(range(10),database['DV'])
ax2a.set_title("Discharge Side Voltage")
ax2a.set_ylabel("Voltage [V]")
ax2b.plot(range(10),database['DI'])
ax2b.set_title("Discharge Side Current")
ax2b.set_ylabel("Current [ma]")

PowerText = StringVar(tabCtl,"0")
ChargeText = StringVar(tabCtl,"0")
DischargeText = StringVar(tabCtl,"0")

graphFrame = Frame(master=tabDat)
graphFrame.pack(side= LEFT)

canvas1 = FigureCanvasTkAgg(fig1,graphFrame)
canvas1.draw()
canvas1.get_tk_widget().pack(side= LEFT)

canvas2 = FigureCanvasTkAgg(fig2,graphFrame)
canvas2.draw()
canvas2.get_tk_widget().pack(side= RIGHT)

measureFrame = Frame(master= tabCtl)
measureFrame.grid(column=0,row=3)

#Label(measureFrame,font=(18), textvariable = ChargeText,fg="black").grid(column=0,row=0)
#Label(measureFrame,font=(18), textvariable = DischargeText,fg="black").grid(column=0,row=1)

# ----------------- Control Tab ----------------


buttonFrame = Frame(master= tabCtl)
buttonFrame.grid(column=2,row=1,padx=20)

changeFrame = Frame(master= tabCtl)
changeFrame.grid(column=0,row=0,pady=10)

## Change axis state
Label(tabCtl,text="Please select duration of operation mode:").grid(column=2,row=0,padx=100)

Button(buttonFrame,text="1 minute",height=2,width=10).grid(column=0,row=1)
Button(buttonFrame,text="5 minutes",height=2,width=10).grid(column=1,row=1)
Button(buttonFrame,text="10 minutes",height=2,width=10).grid(column=2,row=1)

Button(buttonFrame,text="30 minutes",height=2,width=10).grid(column=0,row=2)
Button(buttonFrame,text="1 hour",height=2,width=10).grid(column=1,row=2)
Button(buttonFrame,text="2 hours",height=2,width=10).grid(column=2,row=2)

Button(buttonFrame,text="3 hours",height=2,width=10).grid(column=0,row=3)
Button(buttonFrame,text="4 hours",height=2,width=10).grid(column=1,row=3)
Button(buttonFrame,text="5 hours",height=2,width=10).grid(column=2,row=3)

Button(buttonFrame,text="6 hours",height=2,width=10).grid(column=0,row=4)
Button(buttonFrame,text="7 hours",height=2,width=10).grid(column=1,row=4)
Button(buttonFrame,text="8 hours",height=2,width=10).grid(column=2,row=4)

Button(buttonFrame,text="CANCEL",bg="red",height=2,width=10).grid(column=1,row=5)

##Change charging state
imgChar = PhotoImage(file='modeC.png',master=tabCtl)
imgChar = imgChar.subsample(3,3)
imgDis = PhotoImage(file='modeD.png',master=tabCtl)
imgDis = imgDis.subsample(3,3)
imageMode = Label(master= tabCtl,image=imgChar)
imageMode.grid(column = 0, row = 1)

def switchMode():
    global isMode
    global modeText2

    if isMode == 2: #initialized state
        GPIO.output(charFET,GPIO.HIGH) #Turn on charge-side FET
        modeText2.set("The system is being charged by the solar panel")
        isMode = 0

    elif isMode: #If sytem is in state 1 (discharging), change to state 0 (charging)
        GPIO.output(charFET,GPIO.HIGH) #Turn on charge-side FET
        GPIO.output(disFET,GPIO.LOW) #Turn off discharge-side FET
        imageMode.configure(image= imgChar)
        modeText2.set("The system is being charged by the solar panel")
        isMode = 0

    else: #If sytem is in state 0 (charging), change to state 1 (discharging)
        GPIO.output(charFET,GPIO.LOW) #Turn off charge-side FET
        GPIO.output(disFET,GPIO.HIGH) #Turn on discharge-side FET
        imageMode.configure(image= imgDis)
        modeText2.set("The system is discharging power to the load")
        isMode = 1

modeText2 = StringVar(tabCtl,"Press button to initialize")
Label(changeFrame, textvariable = modeText2,fg="black").grid(column=0,row=0)
Button(changeFrame, command=switchMode, text="Change Charging Mode").grid(column=1,row=0)

Label(tabCtl,text="Manual Motor Control:").grid(column=0,row=2)

motorFrame = Frame(master= tabCtl)
motorFrame.grid(column=0,row=3)

imgArrow1 = PhotoImage(file='cwarrow.png',master=tabCtl)
imgArrow1 = imgArrow1.subsample(20,20)
imgArrow2 = PhotoImage(file='ccwarrow.png',master=tabCtl)
imgArrow2 = imgArrow2.subsample(20,20)
Button(motorFrame,image=imgArrow1,height=60,width=60).grid(column=0,row=1)
Button(motorFrame,image=imgArrow2,height=60,width=60).grid(column=1,row=1)

statusFrame = Frame(master= tabCtl)
statusFrame.grid(column=2,row=2,pady=30)

Label(statusFrame,text="Motor currently operating:",fg="black").grid(column=0,row=0)
Label(statusFrame,text="FALSE",fg="red").grid(column=1,row=0)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ MAIN FUNCTION ~~~~~~~~~~~~~~~~~~~~~~~#

setup()

root.after(0,regen)

root.mainloop()
