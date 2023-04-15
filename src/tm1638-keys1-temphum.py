"""
File:	tm1638-keys1-temphum.py
Date:	20230321
Author:	Robert W.B. Linn
:description
PicoW RESTful webserver listening if key S1 of the TM1638LEDKEY module is pressed.
If pressed, an HTTP API/JSON request is send to Domoticz to get the status of a Temp+Hum device.
The Domoticz server sends a JSON object as response back.
The JSON object is parsed to get the temp and hum values.
These are set on the 8-segment display i.e., 20°C54rH
:log
tm1638-keys1-temphum v20230321
Network connected OK
Network IP picow-ip
Network listening on ('0.0.0.0', 80)
Send GET request url=http://domoticz-ip:port/json.htm?type=devices&rid=15
Send GET request status=OK
Handle request status=1,json={'Sunset': '18:35', 'NautTwilightS ...
Handle request temp=20,hum=54
"""
# Libraries
import network
import socket
import time
from machine import Pin
import json
# Server class from server.py
from server import Server
# Configuration read from config.py (must be uploaded to the picow prior testing)
import config
# TM1638: credits to # https://github.com/mcauser/micropython-tm1638
import tm1638ex
# Constants
NAME	= 'tm1638-keys1-temphum'
VERSION	= 'v20230321'
# Define the url for the HTTP API/JSON GET request
URL_DOM = 'http://' + config.DOMOTICZ_IP + '/json.htm?type=devices&rid={IDX}'
# IDX of the Domoticz temp+hum device
IDX_DEVICE = 15
# Create the LED1 object (as indicator) using config.py settings
led1 = Pin(config.PIN_LED1, Pin.OUT)
led1.value(0)
# Create the tm1638 object with STB = GP13, CLK = GP14, DIO = GP15
tm = tm1638ex.TM1638(stb=Pin(tm1638ex.PIN_STB), clk=Pin(tm1638ex.PIN_CLK), dio=Pin(tm1638ex.PIN_DIO))
# Turn all LEDs off
tm.leds(tm.STATE_OFF)
"""
Handle Request.
The status for the Domoticz temp+hum device is requested from the Domoticz server.
The Domoticz server sends a JSON response back.
The JSON object is parsed to get the temp and hum values.
These are set on the display i.e., 20°C,54rH
During the request handling, LED1 of the Pico W Breadboard is on, but also LED1 of the TM1638 module.
"""
def handle_request(cmd):
    led1.value(1)
    tm.led(tm.LED1, tm.STATE_ON)
    status, content = network.send_get_request(url)
    print(f'Handle request status={status},json={content}')
    if status == 1:
        try:
            # Get key result first array entry
            result = content['result'][0]
            # print(result)
            # Get the properties Temp and Humidity
            temp = int(result['Temp'])
            hum = int(result['Humidity'])
            print(f'Handle request temp={temp},hum={hum}')
            # Set the temp + hum on the display
            tm.temperature(temp,0)
            tm.humidity(hum,4)
        except ValueError as e:
            # print(f'[ERROR] {e}, {r.content.decode()}')
            raise Exception(f'[ERROR] {e}, {r.content.decode()}')
    else:
        tm.show('ERR')
    led1.value(0)
    tm.led(tm.LED1, tm.STATE_OFF)
    
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
            key_nr = i+1
            if key_nr == 1:
                url = URL_DOM.replace('{IDX}', str(IDX_DEVICE))
                handle_request(url)
    time.sleep(.01)
