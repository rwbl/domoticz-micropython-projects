"""
server-test-post.py
20230318 rwbl
PicoW RESTful webserver listening to control an LED via Domoticz Switch.
Commands set via HTTP POST request with HTTP response JSON object.
:commands
LED ON:
curl -v -H "Content-Type: application/json" -d "{\"state\":1}" http://webserver-ip
{"status": "OK", "title": {"state": 1}, "message": 1}
LED OFF:
curl -v -H "Content-Type: application/json" -d "{\"state\":0}" http://webserver-ip
{"status": "OK", "title": {"state": 0}, "message": 0}
NOTE:
When using curl ensure to escape the " to \" in the JSON object.
Thonny Log
LEDControl Network POST v20230310
Network connected OK
Network IP webserver-ip
Network listening on ('0.0.0.0', 80)
Network client connected from NNN.NNN.NNN.94
HTTP Command={'state': 1}
HTTP Response={"status": "OK", "title": {"state": 1}, "message": 1}
Network connection closed
Network client connected from NNN.NNN.NNN.94
HTTP Command={'state': 0}
HTTP Response={"status": "OK", "title": {"state": 0}, "message": 0}
Network connection closed
Network client connected from NNN.NNN.NNN.94
[ERROR] HTTP POST request not valid (ValueError).
HTTP Command={state:vvv}
HTTP Response={"status": "ERROR", "title": "{state:vvv}", "message": "Unknown command."}
Network connection closed
"""
# Libraries
import network
import socket
import time
from machine import Pin
import json
from collections import namedtuple
# Import network class
from server import Server
# Configuration read from config.py (must be uploaded to the picow prior testing)
import config
# Constants
NAME = 'LEDControl Network POST'
VERSION = 'v20230318'
# Create the LED1 object using config.py settings
led1 = Pin(config.PIN_LED1, Pin.OUT)
led1.value(0)
"""
Handle the request containing the command as JSON object.
The LED is turned on or off depending JSON key state {"state":0 or 1}
The response JSON object is updated.
:param string data
    JSON object with key:value pair to set the LED on or off
:return JSON object response
"""
def handle_request(data):
    # Get the JSON key state {"state":0 or 1}
    ledstate = data["state"]
    # Set the led1 state
    led1.value(ledstate)
    # Response is OK
    response[config.KEY_STATE] = config.STATE_OK
    response[config.KEY_MESSAGE] = ledstate
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
        # Parse the post data. In case of error, the status is 0.
        data, status = network.parse_post_request(request)
        
        # Assign the postdata to the response KEY_TITLE
        response[config.KEY_TITLE] = data
        # If status is 1, then the post response is properly parsed, lets change the led state.
        if status == 1:
            response = handle_request(data)
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
        
