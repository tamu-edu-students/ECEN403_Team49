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

import stepper_motor as motor

adc = MCP3008()

cV = 0
cI = 0
cP = 0
dV = 0
dI = 0
dP = 0

isFree = 0
isMode = 2

duration = 10
period = 0
steps = 256 
runningVar = 0

#~~~~~~~~~~~~~~~~~~~ PIN ASSIGNMENTS ~~~~~~~~~~~~~~~~~~~~~~#
charFET = 11
disFET = 13
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


print ("Setting up GPIO pins....")

GPIO.setmode(GPIO.BOARD)
GPIO.setup(charFET,GPIO.OUT) #Setup charge side PFET gpio
GPIO.output(charFET, GPIO.LOW) #Initialize charge PFET to OFF
GPIO.setup(disFET,GPIO.OUT) #Setup discharge side PFET gpio
GPIO.output(disFET, GPIO.LOW) #Initialize discharge PFET to OFF

      # use PHYSICAL GPIO Numbering
for pin in motor.motorPins:
    GPIO.setup(pin,GPIO.OUT)

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

def setDuration(foo):
    global duration
    global runningVar
    global period
    if not runningVar:
        duration = foo
        period = int((duration/256)*1000)
        print ("Time scale set to " + str(duration % 3600) + " hours and " + str(duration % 60) + " minutes.")

def startMotor():
    global steps
    global runningVar
    if not runningVar:
        steps = 256
        runningVar = 1

def stopMotor():
    global runningVar
    steps = 256
    runningVar = 0
    motor.motorStop


def regen():
    count = 0
    global database
    global canvas1
    global line1
    global DischargeText
    global ChargeText
    global duration 
    global steps
    global runningVar
    global period

    global cV,cI,cP,dV,dI,dP

    while True:
        time.sleep(0.05)
        count += 1
        getInput

        if (count % period == 0) and runningVar: #If count
            motor.moveSteps(1,3,1)
            steps = steps - 1
            if (steps <= 0):
                runningVar = 0
            

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

            ax1.cla()
            ax1.plot(range(10),database['CV'],database['CI'])
            ax1.set_ylim(0,4)
            ax1.set_title("Charge Side Voltage")
            ax1.set_ylabel("Voltage [V]")
            canvas1.draw()

            ax2.cla()
            ax2.plot(range(10),database['DV'],database['DI'])
            ax2.set_ylim(0,4)
            ax2.set_title("Discharge Side Voltage")
            ax2.set_ylabel("Voltage [V]")
            canvas2.draw()

        if count % (10 * period) == 0:
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

PowerText = StringVar(tabCtl,"0")
ChargeText = StringVar(tabCtl,"0")
DischargeText = StringVar(tabCtl,"0")

graphFrame = Frame(master=tabDat)
graphFrame.pack(side= LEFT)

#------------------------- Generate Graphs and Database ------------------#
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

canvas1 = FigureCanvasTkAgg(fig1,graphFrame)
canvas1.draw()
canvas1.get_tk_widget().pack(side= TOP)

canvas2 = FigureCanvasTkAgg(fig2,graphFrame)
canvas2.draw()
canvas2.get_tk_widget().pack(side= BOTTOM)

measureFrame = Frame(master= tabCtl)
measureFrame.grid(column=0,row=3)


# ----------------- Control Tab ----------------


buttonFrame = Frame(master= tabCtl)
buttonFrame.grid(column=2,row=1,padx=20)
changeFrame = Frame(master= tabCtl)
changeFrame.grid(column=0,row=0,pady=10)

Label(tabCtl,text="Please select duration of operation mode:").grid(column=2,row=0,padx=100)

Button(buttonFrame,text="5 seconds",height=2,width=10,command=lambda:setDuration(5),).grid(column=0,row=1)
Button(buttonFrame,text="5 minutes",height=2,width=10,command=lambda:setDuration(300)).grid(column=1,row=1)
Button(buttonFrame,text="10 minutes",height=2,width=10,command= lambda:setDuration(600)).grid(column=2,row=1)
Button(buttonFrame,text="30 minutes",height=2,width=10,command=lambda:setDuration(1800)).grid(column=0,row=2)
Button(buttonFrame,text="1 hour",height=2,width=10,command=lambda:setDuration(3600)).grid(column=1,row=2)
Button(buttonFrame,text="2 hours",height=2,width=10,command=lambda:setDuration(7200)).grid(column=2,row=2)
Button(buttonFrame,text="3 hours",height=2,width=10,command=lambda:setDuration(10800)).grid(column=0,row=3)
Button(buttonFrame,text="4 hours",height=2,width=10,command=lambda:setDuration(14400)).grid(column=1,row=3)
Button(buttonFrame,text="5 hours",height=2,width=10,command=lambda:setDuration(18000)).grid(column=2,row=3)
Button(buttonFrame,text="6 hours",height=2,width=10,command=lambda:setDuration(21600)).grid(column=0,row=4)
Button(buttonFrame,text="7 hours",height=2,width=10,command=lambda:setDuration(25200)).grid(column=1,row=4)
Button(buttonFrame,text="8 hours",height=2,width=10,command=lambda:setDuration(28800)).grid(column=2,row=4)
Button(buttonFrame,text="START",bg="green",height=2,width=10,command=startMotor).grid(column=0,row=5)
Button(buttonFrame,text="CANCEL",bg="red",height=2,width=10,command=stopMotor).grid(column=2,row=5)

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
Button(motorFrame,image=imgArrow1,height=60,width=60,command=lambda:motor.moveSteps(1,3,20)).grid(column=0,row=1)
Button(motorFrame,image=imgArrow2,height=60,width=60,command=lambda:motor.moveSteps(0,3,30)).grid(column=1,row=1)

#statusFrame = Frame(master= tabCtl)
#statusFrame.grid(column=2,row=2,pady=30)
#Label(statusFrame,text="Motor currently operating:",fg="black").grid(column=0,row=0)
#Label(statusFrame,text="FALSE",fg="red").grid(column=1,row=0)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ MAIN FUNCTION ~~~~~~~~~~~~~~~~~~~~~~~#

root.after(0,regen)
root.mainloop()