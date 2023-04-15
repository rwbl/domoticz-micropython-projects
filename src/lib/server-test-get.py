"""
server-test-get.py
20230318 rwbl
PicoW RESTful webserver listening to control an LED via Domoticz Switch.
Commands set via HTTP GET request with HTTP response JSON object.
:commands
LED ON:
HTTP Request:	http://picow-ip/led1/on
HTTP response:	{"status": "OK", "title": "/led1/on", "message": "On"}
LED OFF:
HTTP Request:	http://picow-ip/led1/off
HTTP response:	{"status": "OK", "title": "/led1/off", "message": "Off"}
LED STATE:
HTTP Request:	http://picow-ip/led1/state
HTTP response:	{"status": "OK", "title": "/led1/state", "message": "On"}
In case of an error:
HTTP response:	{"status": "ERROR", "title": "/led1/x", "message": "Unknown command."}
Example using curl to turn LED1 on:
curl -v http://picow-ip/led1/on
OR
curl http://webserver-ip/led1/on
{"title": "/led1/on", "message": "On", "status": "OK"}
:log
LEDControl Network GET v20230310
Network connected OK
Network IP webserver-ip
Network listening on ('0.0.0.0', 80)
Network client connected from NNN.NNN.NNN.94
HTTP Command=/led1/on
HTTP Response={"title": "/led1/on", "message": "On", "status": "OK"}
Network connection closed
"""
# Libraries
import network
import socket
import time
from machine import Pin
import json
# Import server class from server.py
from server import Server
# Configuration read from config.py (must be uploaded to the picow prior testing)
import config
# Constants
NAME	= 'LEDControl Network GET'
VERSION = 'v20230318'
# URL params to switch LED1 on or off or request state
# http://pico-ip/command
CMD_LED_ON		= '/led1/on'
CMD_LED_OFF		= '/led1/off'
CMD_LED_STATE	= '/led1/state'
# Create the LED1 object using config.py settings
led1 = Pin(config.PIN_LED1, Pin.OUT)
led1.value(0)
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
        led1.on()
        response[config.KEY_MESSAGE] = config.MESSAGE_ON
        response[config.KEY_STATE] = config.STATE_OK
    # Turn the LED off
    elif cmd == CMD_LED_OFF:
        led1.off()
        response[config.KEY_MESSAGE] = config.MESSAGE_OFF
        response[config.KEY_STATE] = config.STATE_OK
    # Get the LED state
    elif cmd == CMD_LED_STATE:
        if led1.value() == 1:
            response[config.KEY_MESSAGE] = config.MESSAGE_ON
        else:
            response[config.KEY_MESSAGE] = config.MESSAGE_OFF
        response[config.KEY_STATE] = config.STATE_OK
    else:
        response[config.KEY_STATE] = config.STATE_ERR
        response[config.KEY_MESSAGE] = config.MESSAGE_CMD_UNKNOWN                
    return response
# Main
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
