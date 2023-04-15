"""
File:	esp8266-ledblink.py
Date:	20230413
Author:	Robert W.B. Linn
:description
Let LED connected to an ESP8266 pin #D8 (GPIO15) blink every 2 seconds.
:log
esp8266-ledblink v20230413
LED state On
LED state Off
LED state On
"""
# Imports
from machine import Pin
from time import sleep
VERSION = 'esp8266-ledblink v20230413'
# Define the LED pin D8=GPIO15
PIN_LED_D8 = 15
# Create the LED object and set state off
led = Pin(PIN_LED_D8, Pin.OUT)
led.value(0)
# Set blink delay
DELAY = 2	# seconds
def IIF(state):
    """Convert the state 1 | 0 to On | Off string.
    """
    if state == 1:
        return 'On'
    else:
        return 'Off'
print(VERSION)
# Loop forever
while True:
    led.value(not led.value())
    state = led.value()
    
    # Print the led state On or Off
    print('LED state', IIF(led.value()))
    
    # This is not working on the ESP8266
    # print(f'LED state {led.value()}')
    # Wait few seconds
    sleep(DELAY)
