# -*- coding: utf-8 -*-
"""
Created on Sun Jan 29 21:51:35 2023

@author: lpred
"""

from threading import Thread
import time

thread_running = True
user_input = ''

def my_forever_while():
    global thread_running
    # run this while there is no input
    while thread_running:
        n=1
        while(n<513):
            if(user_input != ''):
                break
            moveSteps(1,3,1)
            n=n+1
        time.sleep(0.5)
        n=1
        while(n<513):
            if(user_input != ''):
                break
            moveSteps(0,3,1)
            n=n+1
        time.sleep(0.5)

def take_input():
    global user_input
    user_input = input('Enter any character to stop: ')
    # Input received
    print('Solar Panel Location Set')
    
def panel_charge_rot(rot):
    count = 0
    while(count < 256):
        moveSteps(1,3,1)
        count = count+1
        time.sleep(rot/256 - 3/1000)
    print('Rotation Complete')


if __name__ == '__main__':
    
    setup()
    t1 = Thread(target=my_forever_while)
    t2 = Thread(target=take_input)

    print('Initializing Solar Panel Location')
    t1.start()
    t2.start()

    t2.join()  # interpreter will wait until process gets completed or terminated
    thread_running = False
    print('Rejoin Complete')
    
    print('The minimum rotation time is 30 seconds')
    rot_time = input('Provide rotation time for system in seconds: ')
    if (int(rot_time) < 30):
        print('Rotation Time can not be less than 30 seconds')
        while (int(rot_time) < 30):
            rot_time = input('Please provide a number more than 30 seconds: ')
    else:
        panel_charge_rot(int(rot_time))
    print('Rejoin Complete')
    destroy()
    