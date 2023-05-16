"""
File:	ikeavindriktning.py
Date:	20230515
Author: Robert W.B. Linn
:description
Receive data via UART Serial Communication from the IKEA VINDRIKTNING Air Quality sensor based on particles.
PM2.5 = Particulate Matter 2.5µm Concentration (µg/m3), sensor PM1006.
The sensor sends every ~20 seconds, 5-6 messages which are received over the serial line UART0.
The message buffer received from the sensor must have a length of 20 bytes.
The bytes 5 & 6 are used to calculate the PM2.5 concentration.
An offset is used to update the sensor data in domoticz instead of updating with a value that has not changed.
The air quality value 0-100+ and the air quality level 1 (good), 2 (moderate), 3 (bad) are calculated.
The value is sent via HTTP API/JSON to a Domoticz Custom Sensor.
:data example
b'\x16\x11\x0b\x00\x00\x006\x00\x00\x03`\x00\x00\x02Q\x02\x00\x00\xde\x02'
:log
IKEA VINDRIKTNING v20230515
Network waiting for connection...
Network connected OK
Network IP webserver-ip
Air Quality pm2.5=18 ug/m3, level=1
Send GET request url=http://domoticz-ip:port/json.htm?type=command&param=udevice&idx=46&nvalue=0&svalue=18
Send GET request status=OK
:wiring
IKEA VINDRIKTNING = Pico W
VCC = 5V (Pin #40, VBUS)
GND = GND (Pin #38)
Data = GP17 (Pin #22, UART0 RX) + Voltage divider 5V to 3V3
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
VERSION = 'IKEA VINDRIKTNING v20230515'
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
# IDX of the Domoticz Custom Sensor for the Air Quality
DOM_IDX = 46
# Domoticz API/JSON URL
# The svalue (containing the air quality) is added in the main loop after getting the data from the sensor.
DOM_URL = "http://"+ config.DOMOTICZ_IP +"/json.htm?type=command&param=udevice&idx=" + str(DOM_IDX) + "&nvalue=0&svalue="
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
            network.send_get_request(DOM_URL + str(data[0]))
        # Wait a second
        sleep(1)
