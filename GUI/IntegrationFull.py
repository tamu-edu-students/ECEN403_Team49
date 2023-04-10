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
period = 10/16
steps = 16
runningVar = 0

#~~~~~~~~~~~~~~~~~~~ PIN ASSIGNMENTS ~~~~~~~~~~~~~~~~~~~~~~#
charFET = 11
disFET = 13
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

GPIO.setmode(GPIO.BOARD)
GPIO.setup(charFET,GPIO.OUT) #Setup charge side PFET gpio
GPIO.output(charFET, GPIO.HIGH) #Initialize charge PFET to OFF
GPIO.setup(disFET,GPIO.OUT) #Setup discharge side PFET gpio
GPIO.output(disFET, GPIO.HIGH) #Initialize discharge PFET to OFF

      # use PHYSICAL GPIO Numbering
for pin in motor.motorPins:
    GPIO.setup(pin,GPIO.OUT)

def getInput():

    global PowerText,ChargeText
    global isMode
    global t,cV,cI,cP,dV,dI,dP


    t = time.strftime("%d,%b %H:%M:%S")
    if (isMode == 0): #Charging
      cV = (adc.read(channel=1)) * (5.21/1023.0)
      cI = (adc.read(channel=0)) * (5.21/1023.0) *1000 / (0.005*50)
      cP = cV * cI
      dV = (adc.read(channel=4)) * (5.21/1023.0)
      dI = 0
      dP = 0
    elif (isMode == 1): #Discharging
      cV = (adc.read(channel=1)) * (5.21/1023.0)
      cI = 0
      cP = 0
      dV = (adc.read(channel=4)) * (5.21/1023.0)
      dI = (adc.read(channel=3)) * (5.21/1023.0) *1000 / (0.25*50)
      dP = dV * dI
    else:
      cV = (adc.read(channel=1)) * (5.21/1023.0)
      cI = (adc.read(channel=0)) * (5.21/1023.0) *1000 / (0.005*50)
      cP = cV * cI
      dV = (adc.read(channel=4)) * (5.21/1023.0)
      dI = (adc.read(channel=3)) * (5.21/1023.0) *1000 / (0.25*50)
      dP = dV * dI
    PowerText = str(cP)
    ChargeText = str(dP)
    root.update()

def setDuration(foo):
    global duration
    global runningVar
    global period
    if not runningVar:
        duration = foo
        period = int((duration/16)*100)
        print(period)
        print ("Time scale set to " + str(duration // 3600) + " hours and " + str(duration % 60) + " minutes.")

def startMotor():
    global steps
    global runningVar
    if not runningVar:
        steps = 16
        runningVar = 1
        print("Now Running")

def stopMotor():
    global runningVar
    steps = 16
    runningVar = 0


def regen():
    count = 0
    global database,database2
    global PowerText
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

            database = database.shift(-1)
            database.loc[9] = [cV,cI,dV,dI]

            ax1.cla()
            if (isMode == 1):
                  ax1.plot(range(10),database['DV'],color='r')
            else:
                  ax1.plot(range(10),database['CV'],color='g')
            ax1.set_ylim(0,4.5)
            ax1.set_title("Voltage Measurements")
            ax1.set_ylabel("Voltage [V]")
            canvas1.draw()

            ax2.cla()
            if (isMode == 1):
                  ax2.plot(range(10),database['DI'],color='r')
            else:
                  ax2.plot(range(10),database['CI'],color='g')
            ax2.set_ylim(0,400)
            ax2.set_title("Current Measurements")
            ax2.set_ylabel("Current [A]")
            canvas2.draw()


        if count % 120 == 0:
            file = open("dummyLong.csv","a")
            writer = csv.writer(file)
            data = [t,cV,cI,cP,dV,dI,dP]
            writer.writerow(data)
            file.close()

            database2 = database2.shift(-1)
            if (isMode == 1):
                  foo = ((dV - 3.5) / 0.7) * 100 #Percent of battery charge if 3.5V is 0% (dis side)
            else:
                  foo = ((cV - 3.5) / 0.7) * 100 #Percent of battery charge if 3.5V is 0% (char side)

            if foo < 0:
                foo = 0
            elif foo > 100:
                foo = 100
            database2.loc[99] = [foo]

            ChargeText.set(format(cP,'.4f'))
            DischargeText.set(format(dP,'.4f'))
            PowerText.set(format(foo,'.2f'))

            ax3.cla()
            ax3.plot(range(100),database2[0],color='blue')
            ax3.set_ylim(0,100)
            ax3.set_title("Battery Charge")
            ax3.set_ylabel("%")
            canvas3.draw()



        if count % (120 * period) == 0:
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

PowerText = StringVar(root,"0")
ChargeText = StringVar(root,"0")
DischargeText = StringVar(root,"0")

#------------------------- Generate Graphs and Database ------------------#
d = {'CV':[0,0,0,0,0,0,0,0,0,0],'CI':[0,0,0,0,0,0,0,0,0,0],
    'DV':[0,0,0,0,0,0,0,0,0,0],'DI':[0,0,0,0,0,0,0,0,0,0]}
database = pd.DataFrame(data= d)

database2 = pd.DataFrame(0, index=range(0,100),columns=range(1))

fig1,ax1 = plt.subplots()
fig1.set_size_inches(5,3)
fig1.set_dpi(60)
fig1.set_facecolor("#0F0F0F0F")
ax1.plot(range(10),database['CV'],database['DV'])
ax1.autoscale(False)
ax1.set_title("Voltage Measurements")
ax1.set_ylabel("Voltage [V]")

fig2,ax2 = plt.subplots()
fig2.set_size_inches(5,3)
fig2.set_dpi(60)
fig2.set_facecolor("#0F0F0F0F")
ax2.plot(range(10),database['CI'],database['DI'])
ax2.autoscale(False)
ax2.set_title("Current Measurements")
ax2.set_ylabel("Current [A]")

fig3,ax3 = plt.subplots()
fig3.set_size_inches(5,3)
fig3.set_dpi(60)
fig3.set_facecolor("#0F0F0F0F")
ax3.plot(range(100),database2[0])
ax3.set_title("Battery Storage Tracker")
ax3.set_ylabel("Battery Storage [%]")

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
imgGame = PhotoImage(file='GUI/game.png',master=root)
imgGame = imgGame.subsample(15,15)

measureFrame = Frame(master=tabDat)
measureFrame.grid(column=1,row=1)

Label(measureFrame,font=('Arial',8), textvariable = ChargeText,fg="black").grid(column=1,row=2)
Label(measureFrame,font=('Arial',8), textvariable = PowerText,fg="black").grid(column=3,row=2)
Label(measureFrame,font=('Arial',8), textvariable = DischargeText,fg="black").grid(column=5,row=2)

Label(measureFrame,font=('Arial',8),text= "Power In [W]").grid(column=1,row=1)
Label(measureFrame,font=('Arial',8),text= "Battery Charge [%]").grid(column=3,row=1)
Label(measureFrame,font=('Arial',8),text= "Power Out [W]").grid(column=5,row=1)

Label(master= measureFrame,image=imgPanel).grid(column = 1, row = 0)
Label(master= measureFrame,image=imgArrow).grid(column = 2, row = 0)
Label(master= measureFrame,image=imgBattery).grid(column = 3, row = 0)
Label(master= measureFrame,image=imgArrow).grid(column = 4, row = 0)
Label(master= measureFrame,image=imgGame).grid(column = 5, row = 0)

# ----------------- Animation Tab ----------------
controlFrame = Frame(master=tabAni)
controlFrame.place(anchor="n",x=400,y=25)
animFrame = Frame(master=tabAni)
animFrame.place(anchor='s',x=400,y=350)

# Intialize Frames of Animation as PhotoImages
framesChar = [PhotoImage(master=tabAni,file='chargeAnim/charge%i.png' %(i)) for i in range(1,7)]
for i in range(6):
    framesChar[i] = framesChar[i].subsample(2,2)
    
framesDis = [PhotoImage(master=tabAni,file='dischargeAnim/discharge%i.png' %(i)) for i in range(1,6)]
for i in range(5):
    framesDis[i]= framesDis[i].subsample(2,2)
    
#initialize animation photo in cneter of frame
animation = Label(animFrame,image = None)
animation.grid(column=0,row=0)

#Cycle through the individual frames of the animation
def playChar(i):
    global check                            # ID given to task; Used
    frame = framesChar[i]                   # to reset task when needed
    i += 1
    if i == 6:
        i = 0
    animation.configure(image=frame)        #push next frame
    check = root.after(3000,playChar,i)     #iterate after ~1 sec

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
    if j == 5:
        j = 0
    animation.configure(image=frame)
    check = root.after(3000,playDis,j) 

#Restart Animation frames
def resetDis():
    try:
        root.after_cancel(check)
    except:
        pass 
    animation.configure(image= framesDis[0])
    playDis(0)

# Create buttons to reset animations when pressed
Button(controlFrame, text="Restart Charge Animation",command=resetChar).grid(column=0,row=0,padx=30)
Button(controlFrame, text="Restart Discharge Animation",command=resetDis).grid(column=1,row=0)

# ----------------- Control Tab ----------------

AlphaFrame = Frame(master=tabCtl)
AlphaFrame.place(x=50,y=25)
BetaFrame = Frame(master=tabCtl)
BetaFrame.place(x=500,y=0)

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

Button(beta2,text="10 seconds",height=2,width=10,command=lambda:setDuration(5),).grid(column=0,row=1)
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
        GPIO.output(charFET,GPIO.LOW) #Turn on charge-side FET
        modeText2.set("NOW: Panel charging")
        isMode = 0

    elif isMode: #If sytem is in state 1 (discharging), change to state 0 (charging)
        GPIO.output(charFET,GPIO.LOW) #Turn on charge-side FET
        GPIO.output(disFET,GPIO.HIGH) #Turn off discharge-side FET
        imageMode.configure(image= imgChar)
        modeText2.set("NOW: Panel charging")
        isMode = 0

    else: #If sytem is in state 0 (charging), change to state 1 (discharging)
        GPIO.output(charFET,GPIO.HIGH) #Turn off charge-side FET
        GPIO.output(disFET,GPIO.LOW) #Turn on discharge-side FET
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

motorText = StringVar(tabCtl,"Press button to initialize")
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
