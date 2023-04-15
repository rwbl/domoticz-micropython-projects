"""
rgbled.py
20230318 rwbl
PicoW RESTful webserver listening to control an RGB LED via Domoticz RGB Switch.
Commands set via HTTP GET request with HTTP response JSON object.
:commands
The command is defined as JSON object:
{'level': 0-100, 'red': 0-255, 'green': 0-255, 'blue': 0-255}
curl -v -H "Content-Type: application/json" -d "{\"level\": 18, \"red\": 255, \"green\": 0, \"blue\": 32}" http://webserver-ip
{"status": "OK", "title": {"state": 0}, "message": 0}
NOTE:
When using curl ensure to escape the " to \" in the JSON object.
Thonny Log
RGBLED v20230327
Network IP webserver-ip
Network listening on ('0.0.0.0', 80)
Network client connected from NNN.NNN.NNN.23
HTTP Command={'level': 18, 'red': 255, 'green': 0, 'blue': 32}
HTTP Response={"status": "OK", "title": {"level": 18, "red": 255, "green": 0, "blue": 32}, "message": 18}
Network connection closed
"""
# Libraries
from machine import Pin
import json
# RGBLED extended class
from rgbledex import RGBLEDEX
# Network class
from server import Server
# Configuration read from config.py (must be uploaded to the picow prior testing)
import config
# Constants
NAME = 'RGBLED'
VERSION = 'v20230327'
# Create the RGBLED object
RGB_PIN_RED = const(2)
RGB_PIN_GREEN = const(3)
RGB_PIN_BLUE = const(4)
rgb = RGBLEDEX(RGB_PIN_RED, RGB_PIN_GREEN, RGB_PIN_BLUE)
"""
Handle the request containing the command as JSON object.
Example: {["blue"]=32, ["level"]=78, ["green"]=0, ["red"]=255}
The response JSON object is updated.
:param string data
    JSON object with key:value pair to set the LED on or off
:return JSON object response
"""
def handle_request(data):
    r = data['red']
    g = data['green']
    b = data['blue']
    l = data['level']
    rgb.set_color_brightness(r,g,b,l)
    # Response is OK
    response[config.KEY_STATE] = config.STATE_OK
    response[config.KEY_MESSAGE] = data['level']
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
