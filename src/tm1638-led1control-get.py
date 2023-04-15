"""
File:	tm1638-led1control-get.py
Date:	20230320
Author:	Robert W.B. Linn
:description
PicoW RESTful webserver listening to control the LED1 of the Pico Breadboard Kit via Domoticz Switch.
Commands are set via HTTP GET request with HTTP response JSON object back to the requestor (client).
:commands
LED ON
HTTP Request:	http://picow-ip/led1/on
HTTP response:	{"status": "OK", "title": "/led1/on", "message": "On"}
LED OFF
HTTP Request:	http://picow-ip/led1/off
HTTP response:	{"status": "OK", "title": "/led1/off", "message": "Off"}
LED STATE
HTTP Request:	http://picow-ip/led1/state
HTTP response:	{"status": "OK", "title": "/led1/state", "message": "On"}
In case of an error:
HTTP response:	{"status": "ERROR", "title": "/led1/x", "message": "Unknown command."}
Example using curl to turn LED1 on:
curl -v http://picow-ip/led1/on
:log
TM1638-LED1Control-GET v20230320
Network connected OK
Network IP picow-ip
Network listening on ('0.0.0.0', 80)
Network client connected from client-ip
HTTP Command=/led1/on
HTTP Response={"title": "/led1/on", "message": "On", "status": "OK"}
Network connection closed
Network client connected from client-ip
HTTP Command=/led1/off
HTTP Response={"title": "/led1/off", "message": "Off", "status": "OK"}
Network connection closed
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
NAME = 'TM1638-LED1Control-GET'
VERSION = 'v20230320'
# URL params to switch LED1 on or off or request state
# http://pico-ip/command
CMD_LED_ON		= '/led1/on'
CMD_LED_OFF		= '/led1/off'
CMD_LED_STATE	= '/led1/state'
# Create the LED1 object using config.py settings
led1 = Pin(config.PIN_LED1, Pin.OUT)
led1.value(0)
# Create the tm1638 object with STB = GP13, CLK = GP14, DIO = GP15
tm = tm1638ex.TM1638(stb=Pin(tm1638ex.PIN_STB), clk=Pin(tm1638ex.PIN_CLK), dio=Pin(tm1638ex.PIN_DIO))
# Turn all LEDs off
tm.leds(tm.STATE_OFF)
"""
Handle the request containing the command.
The LED is turned on/off or the state is requested.
The response JSON object is updated.
:param string cmd
    Command to set the LED1 state on/off or get the state.
:return JSON object response
"""
def handle_request(cmd):
    # Turn the LED on
    if cmd == CMD_LED_ON:
        tm.led(tm.LED1, tm.STATE_ON)
        response[config.KEY_MESSAGE] = config.MESSAGE_ON
        response[config.KEY_STATE] = config.STATE_OK
    # Turn the LED off
    elif cmd == CMD_LED_OFF:
        tm.led(tm.LED1, tm.STATE_OFF)
        response[config.KEY_MESSAGE] = config.MESSAGE_OFF
        response[config.KEY_STATE] = config.STATE_OK
    # Get the LED state
    elif cmd == CMD_LED_STATE:
        if tm.led_value(tm.LED1) == 1:
            response[config.KEY_MESSAGE] = config.MESSAGE_ON
        else:
            response[config.KEY_MESSAGE] = config.MESSAGE_OFF
        response[config.KEY_STATE] = config.STATE_OK
    else:
        response[config.KEY_MESSAGE] = config.MESSAGE_CMD_UNKNOWN      
        response[config.KEY_STATE] = config.STATE_ERR
    # Examples getting the LED value 0 or 1
    # print(tm.led_value(0))
    # print(tm.leds_value())
    return response
"""
Main
"""
print(f'{NAME} {VERSION}')
# Create network object
network = Server(config.WIFI_SSID, config.WIFI_PASSWORD)
# Connect to the network and get the server object
server = network.connect()
while True:
    try:
        # Get client connection and the request data
        cl, request = network.get_client_connection(server)
        # Create the HTTP response JSON object
        response = {}
        # Parse the get data. In case of error, the status is 0.
        cmd, status = network.parse_get_request(request)
        
        # Assign the command to the response KEY_TITLE
        response[config.KEY_TITLE] = cmd
        # If the status is 1, handle the command
        if status == 1:
            response = handle_request(cmd)
        else:
            response[config.KEY_STATE] = config.STATE_ERR
            response[config.KEY_MESSAGE] = config.MESSAGE_CMD_UNKNOWN
            
        # Send response to the client and close the connection
        network.send_response(cl, response, True)
    except OSError as e:
        network.ledstatus.off()
        cl.close()
        print('[ERROR] Network Connection closed')
