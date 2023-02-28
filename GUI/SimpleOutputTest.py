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
        count += 1

        if count % 10 == 0:
            t = time.localtime()
            cV = (adc.read(channel=0)) * (5.21/1023.0)
            cI = (adc.read(channel=1)) * (5.21/1023.0)
            cP = cV * cI
            dV = (adc.read(channel=3)) * (5.21/1023.0)
            dI = (adc.read(channel=4)) * (5.21/1023.0)
            dP = dV * dI

            ChargeText = "CV: " + cV + "\t CI: " +cI + "\t CP: " + cP
            DischargeText = "CV: " + cV + "\t CI: " +cI + "\t CP: " + cP



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

tabControl.add(tabCtl, text='Control Systems')
tabControl.pack(expand=1, fill="both")

PowerText = StringVar(tabCtl,"0")
ChargeText = StringVar(tabCtl,"0")
DischargeText = StringVar(tabCtl,"0")

measureFrame = Frame(master= tabCtl)
measureFrame.pack(side= TOP)

Label(measureFrame,font=(18), textvariable = ChargeText,fg="black").grid(column=0,row=0)
Label(measureFrame,font=(18), textvariable = DischargeText,fg="black").grid(column=0,row=1)

# ----------------- Control Tab ----------------

buttonFrame = Frame(master= tabCtl)
buttonFrame.pack(side= BOTTOM)

## Change axis state 

##Change charging state
modeText2 = StringVar(tabCtl,"Press button to initialize")
Label(buttonFrame, textvariable = modeText2,fg="black").grid(column=0,row=1,pady = 50)

def switchMode():
    global isMode
    global modeText2

    if isMode == 2:
        #GPIO.output(charFET,GPIO.HIGH) #Turn on charge-side FET
        modeText2.set("The system is being charged by the solar panel")
        isMode = 0

    elif isMode: #If sytem is in state 1 (discharging), change to state 0 (charging)
        GPIO.output(charFET,GPIO.HIGH) #Turn on charge-side FET
        GPIO.output(disFET,GPIO.LOW) #Turn off discharge-side FET
        modeText2.set("The system is being charged by the solar panel")
        isMode = 0

    else: #If sytem is in state 0 (charging), change to state 1 (discharging)
        GPIO.output(charFET,GPIO.LOW) #Turn off charge-side FET
        GPIO.output(disFET,GPIO.HIGH) #Turn on discharge-side FET
        modeText2.set("The system is discharging power to the load")
        isMode = 1

Button(buttonFrame, command=switchMode, text="Change Charging Mode").grid(column=1,row=2,pady = 50)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ MAIN FUNCTION ~~~~~~~~~~~~~~~~~~~~~~~#

setup()

root.after(0,regen)

root.mainloop()
