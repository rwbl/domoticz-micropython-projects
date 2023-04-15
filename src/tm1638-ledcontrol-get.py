"""
File:	tm1638-ledcontrol-get.py
Date:	20230321
Author:	Robert W.B. Linn
:description
PicoW RESTful webserver listening to control LED1-8 of the TM1638LEDKEY module via Domoticz Switch.
Commands set via HTTP GET request with HTTP response JSON object.
The command can be in any case as converted to lowercase.
:commands
N = LED number 1 to 8 as displayed on the module.
LED ON
HTTP Request:	http://picow-ip/led/N/on
HTTP response:	{"status": "OK", "title": "/led/N/on", "message": "On"}
LED OFF
HTTP Request:	http://picow-ip/led/1/off
HTTP response:	{"status": "OK", "title": "/led/N/off", "message": "Off"}
LED STATE
HTTP Request:	http://picow-ip/led/1/state
HTTP response:	{"status": "OK", "title": "/led/N/state", "message": "On"}
In case of an error:
HTTP response:	{"status": "ERROR", "title": "/led/N/x", "message": "Unknown command."}
Example using curl to turn LED1 on:
curl -v http://picow-ip/led/1/on
:log
TM1638-LEDControl-GET v20230321
Network connected OK
Network IP picow-ip
Network listening on ('0.0.0.0', 80)
Network client connected from client-ip
HTTP Command=/led/8/on
HTTP Response={"title": "/led/8/on", "message": "on", "status": "OK"}
Network connection closed
Network client connected from client-ip
HTTP Command=/led/8/state
HTTP Response={"title": "/led/8/state", "message": "On", "status": "OK"}
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
NAME = 'TM1638-LEDControl-GET'
VERSION = 'v20230321'
# URL params to switch LED1-8 on or off or request state
CMD_LED_ON		= 'on'
CMD_LED_OFF		= 'off'
CMD_LED_STATE	= 'state'
# Create the LED1 object (as indicator) using config.py settings
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
    Command to set the LED1-8 state on/off or get the state.
    The command can be in any case as converted to lowercase.
    Examples: /led/8/on, /led/8/off, /led/8/state
:return JSON object response
    JSON key:value pairs: {"title": <command>, "message": <state>, "status": OK or ERROR}
    Example: {"title": "/led/8/on", "message": "on", "status": "OK"}
"""
def handle_request(cmd):
    # Convert the command to lowercase
    cmd = cmd.lower()
    # Split the command to get the led number and state
    # /led/N/on split into 4 items: '', led, 1-8, on|off|state
    cmd_params = cmd.split('/')
    # Check if the command length is 4
    if len(cmd_params) != 4:
        response[config.KEY_MESSAGE] = f'LED command unknown ({led_cmd}).'
        response[config.KEY_STATE] = config.STATE_ERR
        # raise ValueError(f'LED command unknown ({led_cmd}).')
        return response
    # Get & check the led pos in range 0-7.
    # Note the message is for the led range 1-8 as on the module LED1-LED8
    led_pos = int(cmd_params[2]) - 1
    if not tm.LED_POS_MIN <= led_pos <= tm.LED_POS_MAX:
        response[config.KEY_MESSAGE] = f'LED position {led_pos + 1} out of range {tm.LED_POS_MIN + 1}-{tm.LED_POS_MAX + 1}.'
        response[config.KEY_STATE] = config.STATE_ERR
        # raise ValueError(f'LED Position out of range ({led_pos}).')
        return response
    # Get & check the command on,off,state
    led_cmd = cmd_params[3]
    if not led_cmd in [CMD_LED_ON, CMD_LED_OFF, CMD_LED_STATE]:
        response[config.KEY_MESSAGE] = f'LED command unknown ({led_cmd}).'
        response[config.KEY_STATE] = config.STATE_ERR
        # raise ValueError(f'LED command unknown ({led_cmd}).')
        return response
    # Set the led on or off or get the state
    if led_cmd == CMD_LED_ON:
        tm.led(led_pos, 1)
        response[config.KEY_MESSAGE] = config.MESSAGE_ON
    if led_cmd == CMD_LED_OFF:
        tm.led(led_pos, 0)
        response[config.KEY_MESSAGE] = config.MESSAGE_OFF
    if led_cmd == CMD_LED_STATE:
        if tm.led_value(led_pos) == 1:
            response[config.KEY_MESSAGE] = config.MESSAGE_ON
        else:
            response[config.KEY_MESSAGE] = config.MESSAGE_OFF
    response[config.KEY_STATE] = config.STATE_OK
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
