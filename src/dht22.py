"""
File:   dht22.py
Date:   20230318
Author: Robert W.B. Linn
Read in regular intervals the DHT22 temperature and humidity and update the svalue (i.e., 16;55;1) of a Domoticz device named DHT22.
The Domoticz device is updated using HTTP API/JSON request to the Domoticz server.
:notes
Pico Breadboard Kit is used to wire up the DHT22.
Pico Breadboard Kit LED1 is used as status LED when requesting DHT22 data and updating domoticz.
Configuration stored in config.py, ensure to upload to the picow.
DHT22 measures every 60 seconds.
:log
DHT22 v20230311
Sampling Rate: 60s.
Network connected OK
Network IP webserver-ip
Network listening on ('0.0.0.0', 80)
DHT22 t=19, h=43, hs=0, svalue=19;43;0
Send GET request url=http://domoticz-ip:port/json.htm?type=command&param=udevice&idx=15&nvalue=0&svalue=19;43;0
Send GET request status=OK
:wiring
DHT22 = PicoW
VCC (+) = VBUS (Pin #40)
OUT = GP22 (Pin #29)
GND (-) = GND (Pin #28)
"""
# Imports
from machine import Pin
from utime import sleep
# DHT22 micropython internal lib
from dht import DHT22
# Call server from server.py (must be uploaded to the picow)
from server import Server
# Configuration (must be uploaded to the picow)
import config
# Constants
VERSION = 'DHT22 v20230311'
# Create the led object indicating dht22 measurement in progress
led1 = Pin(config.PIN_LED1, Pin.OUT)
led1.value(0)
    
# DHT22 Signal Pin GP22 #Pin 29
PIN_DHT22 = 22
# DHT22 measurement sampling rate in seconds
SAMPLING_RATE_DHT22 = 60
# DHT22 IDX of the Domoticz Temp+Hum device
IDX_DHT22 = 15
# URL Domoticz
# Note the idx of the domoticz device ( see GUI > Setup > Devices)
# The svalue is added in the main loop after getting the data from the DHT22 module.
# The svalue format: temperature,humidity,humidity status
URL_DOM_DHT22 = "http://"+ config.DOMOTICZ_IP +"/json.htm?type=command&param=udevice&idx=" + str(IDX_DHT22) + "&nvalue=0&svalue="
# Create the dht22 sensor object
dht22_sensor = DHT22(Pin(PIN_DHT22, Pin.IN, Pin.PULL_UP))
"""
Set the humidity status level used for Domoticz HUM_STAT value.
:param int hum
    0: NORMAL, 1: COMFORTABLE, 2: DRY, 3: WET
:return int level
    Humidity level 0 - 3
"""
def set_humidity_status(hum, temp):
    level = 9
    # 2 = Dry
    if hum <= 30:
        level = 2
    # 3 = Wet
    elif hum >= 70:
        level = 3
    # 1 = Comfortable
    elif hum >= 35 and hum <= 65 and temp >=22 and temp <= 26:
        level = 1
    # 0 = Normal
    else:
        level = 0
    return level
"""
DHT22 measurement with roundes values for temperature and humidity.
During measurement, LED1 of the Pico Breadboard is on.
:return string svalue
    svalue with temperature (°C), humidity (0-100%) and humidity_status (0-3)
:example
    16;55;1
"""
def get_dht22_data():
    led1.value(1)
    sleep(1)
    # print(f'DHT22 measuring...')
    dht22_sensor.measure()
    # print(f'DHT22 measuring OK')
    # print(f'DHT22 read data...')
    # Assign the data (rounded)
    temperature     = round(dht22_sensor.temperature())
    humidity        = round(dht22_sensor.humidity())
    humidity_status = set_humidity_status(humidity, temperature)
    # Set the svalue, i.e. svalue=TEMP;HUM;HUM_STAT
    svalue = str(temperature) + ';' + str(humidity) + ';' + str(humidity_status)
    led1.value(0)
    print(f'DHT22 t={temperature}, h={humidity}, hs={humidity_status}, svalue={svalue}')
    return svalue
# Info
print(f'{VERSION}')
print(f'Sampling Rate: {SAMPLING_RATE_DHT22}s.')
# Create network object
network = Server(config.WIFI_SSID, config.WIFI_PASSWORD, DEBUG=True)
# Connect to the network and get the server object
server = network.connect()
# Main
# Measure DHT22 every NN seconds (see constant SAMPLING_DELAY)
while True:
    # Measure DHT22 temperature & humidity & humidity status
    # Submit Domoticz HTTP API/JSON GET request to update the device
    network.send_get_request(URL_DOM_DHT22 + get_dht22_data())
    # Delay till next sample
    sleep(SAMPLING_RATE_DHT22)
