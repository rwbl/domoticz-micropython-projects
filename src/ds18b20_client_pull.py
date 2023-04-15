"""
File:	ds18b20_client_pull.py
Date:	20230413
Author:	Robert W.B. Linn
:description
The Pico W runs as a web server and listens to post request from clients (PULL).
If the post request is {"request":1} then the temperatures of the connected sensors are read.
The data is returned to the client as JSON object in Domoticz format:
{"status": "OK", "title": "{'request': 1}", "message": [{"id": 1, "temperature": 22.0, "address": "28FF5E1804150334"}, {"id": 2, "temperature": 17.4375, "address": "28330A9497040373"}]}
The key message contains an JSON array with the DS18B20 address and temperature.
Each DS18B20 has an unique 8-byte address, like 28 FF 5E 18 04 15 03 34.
The two DS18B20 sensors are:
* Keyes DS18B20 (address 28FF5E1804150334)
* Oumefar Digital Temperaturesensor DS18B20 (address 28330A9497040373)
:example
Using curl with HTTP response JSON object.
HTTP Request
curl -v -H "Content-Type: application/json" -d "{\"request\":1}" http://webserver-ip
HTTP Response
{"status": "OK", "title": "{'request': 1}", "message": [{"id": 1, "temperature": 22.0, "address": "28FF5E1804150334"}, {"id": 2, "temperature": 17.4375, "address": "28330A9497040373"}]}
:notes
Pico Breadboard Kit is used to wire up the DS18B20.
Configuration stored in config.py, ensure to upload to the picow.
DS18B20 measures every 60 seconds.
:log
DS18B20 v20230413
Sampling Rate: 60s.
Network connected OK
Network IP webserver-ip
Network listening on ('0.0.0.0', 80)
One-Wire Devices found: 2
Device: 28FF5E1804150334
Device: 28330A9497040373
-----
Network client connected from NNN.NNN.NNN.94
HTTP Command={'request': 0}
HTTP Response={"status": "ERROR", "title": {"request": 0}, "message": ""}
Network connection closed
Network client connected from NNN.NNN.NNN.94
HTTP Command={'request': 1}
HTTP Response={"status": "OK", "title": "{'request': 1}", "message": [{"id": 1, "temperature": 17.0, "address": "28FF5E1804150334"}, {"id": 2, "temperature": 13.875, "address": "28330A9497040373"}]}
Network connection closed
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
VERSION = 'DS18B20 v20230413'
# Create the led object indicating sensor measurement in progress
led_indicator = Pin(config.PIN_LED1, Pin.OUT)
led_indicator.value(0)
    
# DS18B20 Signal Pin GP15 #Pin 20
PIN_DS18B20 = 15
# Init OneWire with the pin to which one or more DS18B20 sensors are connected
one_wire_bus = Pin(PIN_DS18B20)
# Init the DS18X20 class with constructor function
ds_sensor = DS18X20(OneWire(one_wire_bus))
"""
Read the temperature of the DS18B20 sensor(s).
:return json array
    JSON array with key:value pairs
	[{"id": 1, "temperature": 17.0, "address": "28FF5E1804150334"},
	 {"id": 2, "temperature": 13.875,    "address": "28330A9497040373"}]
"""
def read_ds_sensor():
    # Read & convert temperature
    ds_sensor.convert_temp()
    # Wait: min. 750 ms
    sleep_ms(750)
    # Loop over the devices to get the temperature
    result = []
    id = 0
    for device in devices:
        device_address = bytes(device).hex().upper()
        # print(f'Sensor: {device_address}')
        temperature = ds_sensor.read_temp(device)
        # print(f'Temperatur: {temperature}°C')
        # Add the device address and temperature to the json array
        device = {}
        id = id + 1
        device["id"] = id
        device["address"] = device_address
        device["temperature"] = temperature
        result.append(device);
    # Return the json array with the data
    return result
"""
Handle the request containing the command as JSON object.
The DS18B20 sensor data is read if the command is {"request":1}.
The response JSON object is updated.
:param string data
    JSON object with key:value pair containing the command
:return JSON object response
"""
def handle_request(data):
    # Get the JSON key request {"request":0 or 1}
    request = data["request"]
    if request == 1:
        # Response is OK
        response[config.KEY_STATE] = config.STATE_OK
        response[config.KEY_MESSAGE] = read_ds_sensor()
    else:
        response[config.KEY_STATE] = config.STATE_ERR
        response[config.KEY_MESSAGE] = ""
    return response
# Info
print(f'{VERSION}')
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
while True:
    try:
        # Get client connection and the request data
        cl, request = network.get_client_connection(server)
        # Create the HTTP response JSON object
        response = {}
        # Parse the post data. In case of error, the status is 0.
        data, status = network.parse_post_request(request)
        
        # Assign the postdata to the response KEY_TITLE: {'request': 1} or 0
        response[config.KEY_TITLE] = str(data)
        # If status is 1, then the post response is properly parsed, lets get the sensor data.
        if status == 1:
            response = handle_request(data)
            # HTTP Response={"status": "OK", "title": {"request": 1}, "message": {"28FF5E1804150334": 19.75, "28330A9497040373": 15.5625}}
        else:
            # Error with unknown command
            response[config.KEY_STATE] = config.STATE_ERR
            response[config.KEY_MESSAGE] = config.MESSAGE_CMD_UNKNOWN
        
        # Send response to the client and close the connection
        network.send_response(cl, response, True)
        
    except OSError as e:
        network.ledstatus.off()
        cl.close()
        print('[ERROR] Network Connection closed')
        
