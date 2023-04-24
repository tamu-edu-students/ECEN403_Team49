from MCP3008 import MCP3008
import time
import RPi.GPIO as GPIO

adc = MCP3008()

#https://tutorials-raspberrypi.com/mcp3008-read-out-analog-signals-on-the-raspberry-pi/
#Hook up VDD and VREF to 5V supply on the RPi, not 3.3V
#Also use the MCP3008 class script

def setup():
	print('Starting up test...')
 
def loop():
    while True:
        value = adc.read(channel=0)
        value = (value / 1023.0) * 5.21 #convert digital to analog value
        print('Voltage closed is ', value, ' volts')
        time.sleep(0.5) #wait 0.5s

def destroy():
    GPIO.cleanup()

if __name__ == '__main__':
	setup()
	try:
		loop()
	except KeyboardInterrupt:
		destroy()
		GPIO.cleanup()

         