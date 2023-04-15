"""
File:	tm1638-keys.py
Date:	20230321
Author:	Robert W.B. Linn
:description
PicoW RESTful webserver listening if one of the push buttons S1-S8 of the TM1638LEDKEY module is pressed.
For S1 to S5, an HTTP API/JSON request is send to Domoticz to set an the Level and Text for an Alert Device.
Example: pressing S1 is sets alert level 0 with text "TM1638 Pressed Key S1".
This is a basic example for handling push button press and submit HTTP API/JSON request to Domoticz.
The log shows pressing keys S1 to S5 with HTTP API/JSON request updating level and text for the Alert device with idx 7.
:log
tm1638-keyscontrol v20230321
Network connected OK
Network IP webserver-ip
Network listening on ('0.0.0.0', 80)
Send GET request url=http://domoticz-ip:port/json.htm?type=command&param=udevice&idx=7&nvalue=0&svalue=TM1638 Pressed Key S1
Send GET request status=OK
Send GET request url=http://domoticz-ip:port/json.htm?type=command&param=udevice&idx=7&nvalue=1&svalue=TM1638 Pressed Key S2
Send GET request status=OK
Send GET request url=http://domoticz-ip:port/json.htm?type=command&param=udevice&idx=7&nvalue=2&svalue=TM1638 Pressed Key S3
Send GET request status=OK
Send GET request url=http://domoticz-ip:port/json.htm?type=command&param=udevice&idx=7&nvalue=3&svalue=TM1638 Pressed Key S4
Send GET request status=OK
Send GET request url=http://domoticz-ip:port/json.htm?type=command&param=udevice&idx=7&nvalue=4&svalue=TM1638 Pressed Key S5
Send GET request status=OK
"""
# Libraries
import network
import socket
import time
from machine import Pin
# Server class from server.py
from server import Server
# Configuration read from config.py (must be uploaded to the picow prior testing)
import config
# TM1638: credits to # https://github.com/mcauser/micropython-tm1638
import tm1638ex
# Constants
NAME = 'tm1638-keyscontrol'
VERSION = 'v20230321'
"""
/json.htm?type=command&param=udevice&idx=IDX&nvalue=LEVEL&svalue=TEXT
IDX = id of your device (This number can be found in the devices tab in the column "IDX")
Level = (0=gray, 1=green, 2=yellow, 3=orange, 4=red)
TEXT = Text you want to display
"""
URL_DOM_ALERT_DEVICE = 'http://' + config.DOMOTICZ_IP + '/json.htm?type=command&param=udevice&idx={IDX}&nvalue={LEVEL}&svalue={TEXT}'
IDX_ALERT_DEVICE = 7
# Create the LED1 object (as indicator) using config.py settings
led1 = Pin(config.PIN_LED1, Pin.OUT)
led1.value(0)
# Create the tm1638 object with STB = GP13, CLK = GP14, DIO = GP15
tm = tm1638ex.TM1638(stb=Pin(tm1638ex.PIN_STB), clk=Pin(tm1638ex.PIN_CLK), dio=Pin(tm1638ex.PIN_DIO))
# Turn all LEDs off
tm.leds(tm.STATE_OFF)
"""
Handle Request
"""
def handle_request(cmd):
    print(f'NOT USED')
    
"""
Main
"""
print(f'{NAME} {VERSION}')
# Create network object
network = Server(config.WIFI_SSID, config.WIFI_PASSWORD)
# Connect to the network and get the server object
server = network.connect()
while True:
    # Listen to key pressed    
    pressed = tm.keys()
    
    # Loop over the 8 keys S1-S8
    for i in range(8):
        # Check which key is pressed
        if ((pressed >> i) & 1):
            # Set the LED display with the key number
            tm.number(i+1)
            # tm.show(f'      S{i+1}')
            
            # Send request to Domoticz for the keys 1-5 (index 0-4)
            if 0 <= i <= 4:
                url = URL_DOM_ALERT_DEVICE.replace('{IDX}', str(IDX_ALERT_DEVICE))
                url = url.replace('{LEVEL}', str(i))
                url = url.replace('{TEXT}', f'TM1638 Pressed Key S{i + 1}')
                network.send_get_request(url)
    time.sleep(.01)
