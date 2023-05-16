"""
File:	ikeavindriktning-alert-sensor.py
Date:	20230516
Author: Robert W.B. Linn
:description
Receive data via UART Serial Communication from the IKEA VINDRIKTNING Air Quality sensor based on particles.
PM2.5 = Particulate Matter 2.5µm Concentration (µg/m3).
The air quality value 0-100+ and the air quality level 1 (good), 2 (moderate), 3 (bad) are calculated.
The air quality value is sent via HTTP API/JSON to a Domoticz Custom Sensor.
The air quality level is sent via HTTP API/JSON to a Domoticz Alert Sensor.
This example is an enhancement of ikeavindriktning.py.
:log
IKEA VINDRIKTNING ALERT SENSOR v20230516
Network waiting for connection...
Network connected OK
Network IP picow-ip
Air Quality pm2.5=15 ug/m3, level=1
Send GET request url=http://domoticz-ip:port/json.htm?type=command&param=udevice&idx=46&nvalue=0&svalue=15
Send GET request status=OK
Send GET request url=http://domoticz-ip:port/json.htm?type=command&param=udevice&idx=48&nvalue=1&svalue=GOOD%20(14%20ug/m3)
Send GET request status=OK
"""
# Imports
from machine import Pin,UART
from utime import sleep
# Class IKEAVINDRIKTNING from the library ikeavindriktning.py (must be uploaded to the picow)
from ikeavindriktning import IKEAVINDRIKTNING
# Class server from the library server.py (must be uploaded to the picow)
from server import Server
# Configuration (must be uploaded to the picow)
import config
# Constants
VERSION = 'IKEA VINDRIKTNING ALERT SENSOR v20230516'
"""
PICO W
"""
PIN_UART0_RX = 17   # IKEA VINDRIKTNING UART0 RX Pin GP17 #Pin 22
"""
IKEA VINDRIKTNING SENSOR
"""
UART_BUS = 0        # UART bus 0
VALUE_OFFSET = 2    # Update Domoticz air quality device is abs value between old and new value > offset
# Create an IKEA VINDRIKTNING object
# UART Serial Bus Number 0 or 1, RX pin (default GP17), offset new/old value
iv = IKEAVINDRIKTNING(UART_BUS, PIN_UART0_RX, VALUE_OFFSET)
"""
DOMOTICZ
"""
# Air Quality
# IDX of the Domoticz Custom Sensor for the Air Quality
DOM_IDX_AIR_QUALITY = 46
# Domoticz API/JSON URL
# The svalue (containing the air quality) is added in the main loop after getting the data from the sensor.
DOM_URL_AIR_QUALITY = "http://"+ config.DOMOTICZ_IP +"/json.htm?type=command&param=udevice&idx=" + str(DOM_IDX_AIR_QUALITY) + "&nvalue=0&svalue="
# Air Quality Level
# IDX of the Domoticz Alert Sensor for the Air Quality Level
DOM_IDX_AIR_QUALITY_LEVEL = 48
# Domoticz API/JSON URL
# Level = (1=green, 2=yellow, 3=orange), TEXT = GOOD, MODERATE, BAD.
DOM_URL_AIR_QUALITY_LEVEL = "http://"+ config.DOMOTICZ_IP +"/json.htm?type=command&param=udevice&idx=" + str(DOM_IDX_AIR_QUALITY_LEVEL) + "&nvalue={LEVEL}&svalue={TEXT}"
# Define the 3 air quality levels with text used for the alert sensor text.
# Note the text could be enhanced with the air quality value, i.e. GOOD (19 ug/m3)
air_quality_levels = { 1: "GOOD", 2: "MODERATE", 3: "BAD"}
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
            
            # Submit Domoticz HTTP API/JSON GET requests to update the devices
            # Air Quality Custom Sensor
            url = DOM_URL_AIR_QUALITY + str(data[0])
            network.send_get_request(url)
            # Wait a moment before sending another request
            sleep(1)
            
            # Air Quality Level Alert Sensor
            url = DOM_URL_AIR_QUALITY_LEVEL
            url = url.replace('{LEVEL}', str(data[1]))
            # Option text with level text only i.e., GOOD
            # url = url.replace('{TEXT}', air_quality_levels[data[1]])
            # Option to enhance the text with the air quality value i.e., GOOD (19 ug/m3)
            url = url.replace('{TEXT}', f'{air_quality_levels[data[1]]}%20({str(data[0])}%20ug/m3)')
            network.send_get_request(url)
        # Wait a second
        sleep(1)
