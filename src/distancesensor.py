"""
File:   distancesensor.py
Date:   20230512
Author: Robert W.B. Linn
:description
Read in regular intervals the distance using a HC-SR04 sensor and update the svalue (i.e., 20.132) of a Domoticz Distance device.
The Domoticz device from type general, distance, is updated using HTTP API/JSON request to the Domoticz server.
/json.htm?type=command&param=udevice&idx=IDX&nvalue=0&svalue=DISTANCE
IDX = device id, DISTANCE = distance in cm or inches with decimals.
    
:external libraries
hcsr04 (https://github.com/rsc1975/micropython-hcsr04)
:notes
Configuration stored in config.py, ensure to upload to the pico.
Distance sensor measures every NN seconds.
:log
Distance Sensor v20230512
Sampling Rate: 10s.
Network waiting for connection...
Network connected OK
Network IP picow-ip
Send GET request url=http://domoticz-ip:port/json.htm?type=command&param=udevice&idx=44&nvalue=0&svalue=10.9
Send GET request status=OK
:wiring
Abbreviation: LLC = Logic Level Converter (3.3V-5V)
LLC = Pico W
LV1 = N/A
LV2 = N/A
LV	= 3V3 (OUT)
GND	= GND (Pin #38)
LV3 = GP14 (Pin #19)
LV4 = GP15 (Pin #20)
HV1 = N/A
HV2 = N/A
HV	= VBUS (Pin #40)
GND	= GND (Pin #38)
HV3	= N/A
HV4	= N/A
LLC = HC-SR04
LV1 = N/A
LV2 = N/A
LV	= N/A
GND	= N/A
LV3 = N/A
LV4 = N/A
HV1 = N/A
HV2 = N/A
HV	= VCC
GND	= GND
HV3	= Echo
HV4	= Trig
"""
# Imports
from machine import Pin
from utime import sleep
# HCSR04 from hcsr04.py (must be uploaded to the pico)
from hcsr04 import HCSR04
# Server from server.py (must be uploaded to the pico)
from server import Server
# Configuration (must be uploaded to the picow)
import config
# Constants
VERSION = 'Distance Sensor v20230512'
"""
DOMOTICZ
"""
# Distance Sensor IDX of the Domoticz Temp+Hum device
IDX_DISTANCE = 44
# URL Domoticz
# The svalue is added in the main loop after getting the data from the distance sensor.
# The svalue format: distance
URL_DOM = "http://"+ config.DOMOTICZ_IP +"/json.htm?type=command&param=udevice&idx=" + str(IDX_DISTANCE) + "&nvalue=0&svalue="
"""
DISTANCESENSOR HC-SR04
"""
# Sensor Pins
PIN_ECHO = 14
PIN_TRIG = 15
distance_sensor = HCSR04(trigger_pin=PIN_TRIG, echo_pin=PIN_ECHO)
"""
SAMPLING
"""
# Distance measurement sampling rate in seconds
SAMPLING_RATE = 10
# Info
print(f'{VERSION}')
print(f'Sampling Rate: {SAMPLING_RATE}s.')
# Create network object
network = Server(config.WIFI_SSID, config.WIFI_PASSWORD, DEBUG=True)
# Connect to the network and get the server object
server = network.connect2()
# Main
while True:
    # Measure the distance in cm
    try:
        distance = distance_sensor.distance_cm()
    except OSError as e:
        print(f'[ERROR] Can not get the distance {e}')
    # Submit Domoticz HTTP API/JSON GET request to update the device
    network.send_get_request(URL_DOM + str(distance))
    # Delay till next sample
    sleep(SAMPLING_RATE)
