# -*- coding: utf-8 -*-
"""
Created on Sun Jan 29 21:21:30 2023

@author: lpred
Sample code on threads for single axis mode solar panel location initialization
"""
from threading import Thread
import time

thread_running = True
user_input = ''

def my_forever_while():
    global thread_running

    start_time = time.time()

    # run this while there is no input
    while thread_running:
        n=0
        while(n<5):
            if(user_input != ''):
                break
            print('1')
            time.sleep(1)
            n=n+1
        n=0
        while(n<5):
            if(user_input != ''):
                break
            print(2)
            time.sleep(1)
            n=n+1
#        time.sleep(0.1)

#        if time.time() - start_time >= 5:
#            start_time = time.time()
#            print('Another 5 seconds has passed')


def take_input():
    global user_input
    user_input = input('Type user input: ')
    # doing something with the input
    print('The user input is: ', user_input)


if __name__ == '__main__':
    t1 = Thread(target=my_forever_while)
    t2 = Thread(target=take_input)

    t1.start()
    t2.start()

    t2.join()  # interpreter will wait until your process get completed or terminated
    thread_running = False
    print('The end')