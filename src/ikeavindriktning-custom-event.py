"""
File:	ikeavindriktning-custom-event.py
Date:	20230515
Author: Robert W.B. Linn
:description
Receive data via UART Serial Communication from the IKEA VINDRIKTNING Air Quality sensor based on particles.
PM2.5 = Particulate Matter 2.5µm Concentration (µg/m3).
The air quality value 0-100+ and the air quality level 1 (good), 2 (moderate), 3 (bad) are calculated.
The air quality value and level are sent via HTTP API/JSON POST request to a Domoticz Custom Event.
This example is an enhancement of ikeavindriktning.py.
:log
"""
# Imports
from machine import Pin,UART
from utime import sleep
# Class IKEAVINDRIKTNING from the lib ikeavindriktning.py - stored in Pico W folder lib
from ikeavindriktning import IKEAVINDRIKTNING
# Class Server from the library server.py - stored in Pico W folder lib
from server import Server
# Configuration (must be uploaded to the picow)
import config
# Constants
VERSION = 'IKEA VINDRIKTNING CUSTOM EVENT v20230516'
"""
PICO W
"""
PIN_UART0_RX = 17   # IKEA VINDRIKTNING UART0 RX Pin GP17 #Pin 22
"""
IKEA VINDRIKTNING SENSOR
"""
UART_BUS = 0        # UART bus 0
VALUE_OFFSET = 0    # Update Domoticz air quality device is abs value between old and new value > offset
# Create an IKEA VINDRIKTNING object
# UART Serial Bus Number 0 or 1, RX pin (default GP17), offset new/old value
iv = IKEAVINDRIKTNING(UART_BUS, PIN_UART0_RX, VALUE_OFFSET)
"""
DOMOTICZ
"""
# Domoticz API/JSON URL for the custom event handled by POST request.
# The postdata is added after having the data received: {"value":NN,"level":N}
DOM_URL = "http://"+ config.DOMOTICZ_IP +"/json.htm?type=command&param=customevent&event=airquality&data="
# Info
print(f'{VERSION}')
# Create network object
network = Server(config.WIFI_SSID, config.WIFI_PASSWORD, DEBUG=True)
# Connect to the network and get the server object
server = network.connect2()
# Loop forever
while True:
    
    # Check if there is data send from the sensor via serial line
    if iv.uart.any():
        # Get the air quality & air quality level as dict
        data = iv.air_quality_data(iv.uart.read())
        
        # Check if the dict contains data - only if above offset 
        if data != None:
            # Log the air quality & level from the data dict
            print(f'Air Quality pm2.5={data[0]} ug/m3, level={data[1]}')
            
            # Submit Domoticz HTTP API/JSON GET request to update the device
            # Post data
            postdata = {}
            postdata['value'] = data[0]
            postdata['level'] = data[1]
            # Submit domoticz
            status = network.send_post_request(DOM_URL, postdata)
        # Wait a second
        sleep(1)
