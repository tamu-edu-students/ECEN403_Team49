import pandas as pd #Pandas for database creation
import time
import random
import csv

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
t = 0

isFree = 0
isMode = 2

duration = 10
period = 10/256
steps = 256 
runningVar = 0

#~~~~~~~~~~~~~~~~~~~ PIN ASSIGNMENTS ~~~~~~~~~~~~~~~~~~~~~~#
charFET = 11
disFET = 13
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

GPIO.setmode(GPIO.BOARD)
GPIO.setup(charFET,GPIO.OUT) #Setup charge side PFET gpio
GPIO.output(charFET, GPIO.LOW) #Initialize charge PFET to OFF
GPIO.setup(disFET,GPIO.OUT) #Setup discharge side PFET gpio
GPIO.output(disFET, GPIO.LOW) #Initialize discharge PFET to OFF

      # use PHYSICAL GPIO Numbering
for pin in motor.motorPins:
    GPIO.setup(pin,GPIO.OUT)

def getInput():

    global isMode
    global t,cV,cI,cP,dV,dI,dP


    t = time.strftime("%d,%b %H:%M:%S")
    if (isMode == 0): #Charging
      cV = (adc.read(channel=0)) * (5.21/1023.0)
      cI = (adc.read(channel=1)) * (5.21/1023.0) *1000 / (0.005*50)
      cP = cV * cI
      dV = (adc.read(channel=3)) * (5.21/1023.0)
      dI = 0
      dP = 0
    elif (isMode == 1): #Discharging
      cV = (adc.read(channel=0)) * (5.21/1023.0)
      cI = 0
      cP = 0
      dV = (adc.read(channel=3)) * (5.21/1023.0)
      dI = (adc.read(channel=4)) * (5.21/1023.0) *1000 / (0.25*50)
      dP = dV * dI
    else:
      cV = (adc.read(channel=0)) * (5.21/1023.0)
      cI = (adc.read(channel=1)) * (5.21/1023.0) *1000 / (0.005*50)
      cP = cV * cI
      dV = (adc.read(channel=3)) * (5.21/1023.0)
      dI = (adc.read(channel=4)) * (5.21/1023.0) *1000 / (0.25*50)
      dP = dV * dI
    #root.update()

def setDuration(foo):
    global duration
    global runningVar
    global period
    if not runningVar:
        duration = foo
        period = int((duration/16)*100)
        print ("Time scale set to " + str(duration // 3600) + " hours and " + str(duration % 60) + " minutes.")

def startMotor():
    global steps
    global runningVar
    if not runningVar:
        steps = 16
        runningVar = 1

def stopMotor():
    global runningVar
    steps = 16
    runningVar = 0


def regen():
    count = 0
    global database
    global DischargeText
    global ChargeText
    global duration 
    global steps
    global runningVar
    global period

    global cV,cI,cP,dV,dI,dP,t

    while True:
        count += 1
        getInput()

        if (count % period == 0) and runningVar: #If count
            motor.moveSteps(1,3,16)
            steps = steps - 1
            if (steps <= 0):
                runningVar = 0
            

        if count % 10 == 0:

            #ChargeText = "CV: " + str(cV) + "\t CI: " + str(cI) + "\t CP: " + str(cP)
            #DischargeText = "CV: " + str(cV) + "\t CI: " + str(cI) + "\t CP: " + str(cP)

            database = database.shift(-1)
            database.loc[9] = [cV,cI,dV,dI]

            ax1.cla()
            if (isMode == 1):
                  ax1.plot(range(10),database['DV'])
            else:
                  ax1.plot(range(10),database['CV'])
            ax1.set_ylim(0,4.5)
            ax1.set_title("Voltage Measurements")
            ax1.set_ylabel("Voltage [V]")
            canvas1.draw()

            ax2.cla()
            if (isMode == 1):
                  ax2.plot(range(10),database['DI'])
            else:
                  ax2.plot(range(10),database['CI'])
            ax2.set_ylim(0,0.4)
            ax2.set_title("Current Measurements")
            ax2.set_ylabel("Current [A]")
            canvas2.draw()


        if count % 100 == 0:
            file = open("dummyLong.csv","a")
            writer = csv.writer(file)
            data = [t,cV,cI,cP,dV,dI,dP]
            writer.writerow(data)
            file.close()
            dataLong = pd.read_csv("dummyLong.csv")
            #pd.concat([dataLong,pd.Series([1,1,1,1,1,1,1])])
            #dataLong.append([t,cV,cI,cP,dV,dI,dP])
            #print("Adding to database...")
            #print(dataLong)



        if count % (100 * period) == 0:
            count = 0
        
        root.update()
           
        
root = Tk()
#root.geometry("800x480")
root.title("MCU to Graph Test")
#root.maxsize(800,480)
tabControl = ttk.Notebook(root)
tabCtl = Frame(tabControl)
tabDat = Frame(tabControl)
tabAni = Frame(tabControl)
tabControl.add(tabDat, text='System Data')
tabControl.pack(expand=1, fill="both")
tabControl.add(tabCtl, text='Control Systems')
tabControl.pack(expand=1, fill="both")
tabControl.add(tabAni, text='System Animation')
tabControl.pack(expand=1, fill="both")

PowerText = StringVar(tabCtl,"0")
ChargeText = StringVar(tabCtl,"0")
DischargeText = StringVar(tabCtl,"0")

#------------------------- Generate Graphs and Database ------------------#
d = {'CV':[0,0,0,0,0,0,0,0,0,0],'CI':[0,0,0,0,0,0,0,0,0,0],
    'DV':[0,0,0,0,0,0,0,0,0,0],'DI':[0,0,0,0,0,0,0,0,0,0]}
database = pd.DataFrame(data= d)

d1 = {'P':[0,10,12,14,16,17,18,20,23,27,32,45,50,53,60,59,64,73,79,80,82,81,80,81,79,65,43,24,10,11,12]}
database1 = pd.DataFrame(data= d1)

fig1,ax1 = plt.subplots()
fig1.set_size_inches(5,3)
fig1.set_dpi(60)
ax1.plot(range(10),database['CV'],database['DV'])
ax1.autoscale(False)
ax1.set_title("Voltage Measurements")
ax1.set_ylabel("Voltage [V]")

fig2,ax2 = plt.subplots()
fig2.set_size_inches(5,3)
fig2.set_dpi(60)
ax2.plot(range(10),database['CI'],database['DI'])
ax2.autoscale(False)
ax2.set_title("Current Measurements")
ax2.set_ylabel("Current [A]")

fig3,ax3 = plt.subplots()
fig3.set_size_inches(5,3)
fig3.set_dpi(60)
ax3.plot(range(31),database1['P'])
ax3.autoscale(True)
ax3.set_title("Battery Storage Tracker")
ax3.set_ylabel("Battery Storage [%]")

#dataFrame = Frame(master=tabDat).grid(row=0,column=0)

canvas1 = FigureCanvasTkAgg(fig1,tabDat)
canvas1.draw()
canvas1.get_tk_widget().grid(row=0,column=0)

canvas2 = FigureCanvasTkAgg(fig2,tabDat)
canvas2.draw()
canvas2.get_tk_widget().grid(row=1,column=0)

canvas3 = FigureCanvasTkAgg(fig3,tabDat)
canvas3.draw()
canvas3.get_tk_widget().grid(row=0,column=1)

PowerText = StringVar(root,"0")
ChargeText = StringVar(root,"0")

imgPanel = PhotoImage(file='panel.png',master=root)
imgPanel = imgPanel.subsample(3,3)
imgArrow = PhotoImage(file='arrow.png',master=root)
imgArrow = imgArrow.subsample(40,40)
imgBattery = PhotoImage(file='battery.png',master=root)
imgBattery = imgBattery.subsample(7,7)

measureFrame = Frame(master=tabDat)
measureFrame.grid(column=1,row=1)

Label(measureFrame,font=(14), textvariable = PowerText,fg="black").grid(column=1,row=2)
Label(measureFrame,font=(14), textvariable = ChargeText,fg="black").grid(column=3,row=2)

Label(measureFrame,font=(14),text= "Charge-side Power [W]").grid(column=1,row=1)
Label(measureFrame,font=(14),text= "Battery Charge [%]").grid(column=3,row=1)

Label(master= measureFrame,image=imgPanel).grid(column = 1, row = 0)
Label(master= measureFrame,image=imgArrow).grid(column = 2, row = 0)
Label(master= measureFrame,image=imgBattery).grid(column = 3, row = 0)

dataLong = pd.read_csv("dummyLong.csv")

# ----------------- Animation Tab ----------------
ttk.Label(tabAni, text='Here we display our system animation').grid(column=0, row=0, padx=0, pady=10)

def resetChar():
    return
def resetDis():
    return

Button(tabAni, text="Restart Charge Animation",command=resetChar).grid(column=0,row=1,padx=30)
Button(tabAni, text="Restart Discharge Animation",command=resetDis).grid(column=1,row=1)

# ----------------- Control Tab ----------------

AlphaFrame = Frame(master=tabCtl)
AlphaFrame.grid(column=0,row=0,padx=60)
BetaFrame = Frame(master=tabCtl)
BetaFrame.grid(column=1,row=0)

alpha1 = Frame(master= AlphaFrame)
alpha1.grid(row=0)
alpha2 = Frame(master= AlphaFrame)
alpha2.grid(row=1)
alpha3 = Frame(master= AlphaFrame)
alpha3.grid(row=2)
alpha4 = Frame(master= AlphaFrame)
alpha4.grid(row=3)

beta1 = Frame(master= BetaFrame)
beta1.grid(row=0)
beta2 = Frame(master= BetaFrame)
beta2.grid(row=1)
beta3 = Frame(master= BetaFrame)
beta3.grid(row=2)
beta4 = Frame(master= BetaFrame)
beta4.grid(row=3)


Label(beta1,text="Please select duration of operation mode:").grid(column = 0, row=0)

Button(beta2,text="5 seconds",height=2,width=10,command=lambda:setDuration(5),).grid(column=0,row=1)
Button(beta2,text="5 minutes",height=2,width=10,command=lambda:setDuration(300)).grid(column=1,row=1)
Button(beta2,text="10 minutes",height=2,width=10,command= lambda:setDuration(600)).grid(column=2,row=1)
Button(beta2,text="30 minutes",height=2,width=10,command=lambda:setDuration(1800)).grid(column=0,row=2)
Button(beta2,text="1 hour",height=2,width=10,command=lambda:setDuration(3600)).grid(column=1,row=2)
Button(beta2,text="2 hours",height=2,width=10,command=lambda:setDuration(7200)).grid(column=2,row=2)
Button(beta2,text="3 hours",height=2,width=10,command=lambda:setDuration(10800)).grid(column=0,row=3)
Button(beta2,text="4 hours",height=2,width=10,command=lambda:setDuration(14400)).grid(column=1,row=3)
Button(beta2,text="5 hours",height=2,width=10,command=lambda:setDuration(18000)).grid(column=2,row=3)
Button(beta2,text="6 hours",height=2,width=10,command=lambda:setDuration(21600)).grid(column=0,row=4)
Button(beta2,text="7 hours",height=2,width=10,command=lambda:setDuration(25200)).grid(column=1,row=4)
Button(beta2,text="8 hours",height=2,width=10,command=lambda:setDuration(28800)).grid(column=2,row=4)
Button(beta2,text="START",bg="green",height=2,width=10,command=startMotor).grid(column=0,row=5)
Button(beta2,text="CANCEL",bg="red",height=2,width=10,command=stopMotor).grid(column=2,row=5)

##Change charging state
imgChar = PhotoImage(file='modeC.png',master=root)
imgChar = imgChar.subsample(4,4)
imgDis = PhotoImage(file='modeD.png',master=root)
imgDis = imgDis.subsample(4,4)
imageMode = Label(master= alpha2,image=imgChar)
imageMode.grid(column=0,row=0)

imgFixed = PhotoImage(file='panelFixed.png',master=root)
imgFixed = imgFixed.subsample(4,4)
imgFree = PhotoImage(file='panelFree.png',master=root)
imgFree = imgFree.subsample(4,4)
imageAngle = Label(master= alpha4,image=imgFixed)
imageAngle.grid(column=0, row=0)

def switchMode():
    global isMode
    global modeText2

    if isMode == 2: #initialized state
        GPIO.output(charFET,GPIO.HIGH) #Turn on charge-side FET
        modeText2.set("NOW: Panel charging")
        isMode = 0

    elif isMode: #If sytem is in state 1 (discharging), change to state 0 (charging)
        GPIO.output(charFET,GPIO.HIGH) #Turn on charge-side FET
        GPIO.output(disFET,GPIO.LOW) #Turn off discharge-side FET
        imageMode.configure(image= imgChar)
        modeText2.set("NOW: Panel charging")
        isMode = 0

    else: #If sytem is in state 0 (charging), change to state 1 (discharging)
        GPIO.output(charFET,GPIO.LOW) #Turn off charge-side FET
        GPIO.output(disFET,GPIO.HIGH) #Turn on discharge-side FET
        imageMode.configure(image= imgDis)
        modeText2.set("NOW: Battery discharging")
        isMode = 1

modeText2 = StringVar(tabCtl,"Press button to initialize")
Label(alpha1, textvariable = modeText2,fg="black").grid(column=0,row=0)
Button(alpha1, command=switchMode, text="Change Charging Mode").grid(column=1,row=0)

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

modeText1 = StringVar(tabCtl,"Press button to initialize")
Label(alpha3, textvariable = modeText1,fg="black").grid(column=0,row=0)
Button(alpha3, command=switchFree, text="Change Axis Mode").grid(column=1,row=0)

Label(beta3,text="Motor currently operating:",fg="black").grid(column=0,row=0)
Label(beta3,text="FALSE",fg="red").grid(column=1,row=0)
Label(beta3,text="Manual Motor Control:").grid(column=0,row=1)

imgArrow1 = PhotoImage(file='cwarrow.png',master=tabCtl)
imgArrow1 = imgArrow1.subsample(20,20)
imgArrow2 = PhotoImage(file='ccwarrow.png',master=tabCtl)
imgArrow2 = imgArrow2.subsample(20,20)
Button(beta4,image=imgArrow1,height=60,width=60,command=lambda:motor.moveSteps(1,3,20)).grid(column=0,row=1)
Button(beta4,image=imgArrow2,height=60,width=60,command=lambda:motor.moveSteps(0,3,30)).grid(column=1,row=1)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ MAIN FUNCTION ~~~~~~~~~~~~~~~~~~~~~~~#

root.after(0,regen)
root.mainloop()
