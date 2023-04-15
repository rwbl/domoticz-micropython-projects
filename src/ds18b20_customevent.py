"""
File:	ds18b20_customevent.py
Date:	20230412
Author:	Robert W.B. Linn
:description
Read in regular intervals the temperature of two DS18B20 devices and update the temperature of the Domoticz devices named DS18B20-1, DS18B20-2.
Each DS18B20 has an unique 8-byte address, like 28 FF 5E 18 04 15 03 34.
The two DS18B20 sensors are:
* Keyes DS18B20 (address 28FF5E1804150334)
* Oumefar Digital Temperaturesensor DS18B20 (address 28330A9497040373)
The Domoticz devices are updated from a Domoticz Custom Event (dzVents) triggered by a HTTP API/JSON CustomEvent request to the Domoticz server.
Example:
http://domoticz-ip:port/json.htm?type=command&param=customevent&event=DS18B20&data={'X28FF5E1804150334': 16.5, 'X28330A9497040373': 15.25}
:notes
Pico Breadboard Kit is used to wire up the DS18B20.
Configuration stored in config.py, ensure to upload to the picow.
DS18B20 measures every 60 seconds.
:log
DS18B20 v20230412
Sampling Rate: 60s.
Network connected OK
Network IP picow-ip
Network listening on ('0.0.0.0', 80)
One-Wire Devices found: 2
Device: 28FF5E1804150334
Device: 28330A9497040373
-----
Send POST request url=http://domoticz-ip:port/json.htm?type=command&param=customevent&event=DS18B20&data=, postdata={'X28FF5E1804150334': 16.5, 'X28330A9497040373': 15.25}
Send POST request status=OK
:wiring
DS18B20 = Raspberry Pi Pico W
VDD = 3V3 (Pin #36)
GND = GND (Pin #38)
Data = GP15 (Pin #20)
The wiring applies to N sensors.
"""
# Imports
from machine import Pin
from utime import sleep, sleep_ms
# The onewire and ds18x20 are micropython internal libs.
from onewire import OneWire
from ds18x20 import DS18X20
import json
# Call server from server.py (must be uploaded to the picow)
from server import Server
# Configuration (must be uploaded to the picow)
import config
# Constants
VERSION = 'DS18B20 v20230412'
# Create the led object indicating sensor measurement in progress
led_indicator = Pin(config.PIN_LED1, Pin.OUT)
led_indicator.value(0)
    
# DS18B20 Signal Pin GP15 #Pin 20
PIN_DS18B20 = 15
# DS18B20 measurement sampling rate in seconds
SAMPLING_RATE = 60
# URL Domoticz
URL_DOM = "http://"+ config.DOMOTICZ_IP +"/json.htm?type=command&param=customevent&event=DS18B20&data="
# Init OneWire with the pin to which one or more DS18B20 sensors are connected
one_wire_bus = Pin(PIN_DS18B20)
# Init the DS18X20 class with constructor function
ds_sensor = DS18X20(OneWire(one_wire_bus))
"""
Read the temperature of the DS18B20 sensor(s).
:return json array
    JSON array with key:value pairs {"device address":temperature, ...}
    NOTE: The device address has prefix X to get handled by the Domoticz dzVents custom event.
    {'X28FF5E1804150334': 16.5, 'X28330A9497040373': 15.1875}
"""
def read_ds_sensor():
    # Read & convert temperature
    ds_sensor.convert_temp()
    # Wait: min. 750 ms
    sleep_ms(750)
    # Loop over the devices to get the temperature
    result = {}
    for device in devices:
        device_address = 'X' + bytes(device).hex().upper()
        # print(f'Sensor: {device_address}')
        temperature = ds_sensor.read_temp(device)
        # print(f'Temperatur: {temperature}°C')
        # Add the device address and temperature to the json array
        result[device_address] = temperature
    # Return the json array with the data
    return result
# Info
print(f'{VERSION}')
print(f'Sampling Rate: {SAMPLING_RATE}s.')
# Create network object
network = Server(config.WIFI_SSID, config.WIFI_PASSWORD, DEBUG=True)
# Connect to the network and get the server object
server = network.connect()
# Scan for One-Wire devices
# Get list of ROM addresses for all of the attached slaves. Each ROM address is an 8-byte long bytearray.
devices = ds_sensor.scan()
print(f'One-Wire Devices found: {len(devices)}')
for device in devices:
    print(f'Device: {bytes(device).hex().upper()}')
print(f'-----')
# Main
# Measure every NN seconds (see constant SAMPLING_DELAY)
while True:
    led_indicator.value(1)
    # Read the sensor(s)
    data = read_ds_sensor()
    # print(f'{data}')
    # Submit Domoticz HTTP API/JSON POST request to update the devices via customevent
    network.send_post_request(URL_DOM, data)
    led_indicator.value(0)
    # Delay till next sample
    sleep(SAMPLING_RATE)
