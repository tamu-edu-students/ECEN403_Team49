from MCP3008 import MCP3008
import time
import RPi.GPIO as GPIO

adc = MCP3008() #initialize adc
switchPin = 11 #gpio pin for pfet

def setup():
	print('Starting up test...')
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(switchPin, GPIO.OUT)
	GPIO.output(switchPin, GPIO.LOW)

def loop():
    while True:
        GPIO.output(switchPin, GPIO.HIGH)
        value = adc.read(channel=0)
        value = (value / 1023.0) * 5.21 #convert digital to analog value
        time.sleep(1) #wait 0.5s
        curr = adc.read(channel=1)
        curr = (curr / 1023.0) * 5.21 *1000 / (10*50) #convert to mA
        print('Voltage closed is ', value, ' volts')
        print('Current closed is ', curr, ' mA')
        print('Power when switch closed is', value*curr, ' mW') #compute power
        time.sleep(1) #wait 1 second
        GPIO.output(switchPin, GPIO.LOW)
        value = adc.read(channel=0)
        value = (value / 1023.0) * 5.21 #convert digital to analog value
        time.sleep(1) #wait 0.5s
        curr = adc.read(channel=1)
        curr = (curr / 1023.0) * 5.21 *1000 / (10*50) #convert to mA
        print('Voltage open is ', value, ' volts')
        print('Current open is ', curr, ' mA')
        print('Power when switch open is', value*curr, ' mW') #compute power
        time.sleep(1) #wait 1 second

def destroy():
    GPIO.cleanup()


if __name__ == '__main__':
	setup()
	try:
		loop()
	except KeyboardInterrupt:
		destroy()

