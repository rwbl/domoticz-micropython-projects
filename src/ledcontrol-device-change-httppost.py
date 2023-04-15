"""
File:	ledcontrol-device-change-httppost.py
Date:	20230409
Author: Robert W.B. Linn
PicoW RESTful webserver listening to set the state of an LED.
The states are: on, off, toggle, blink, pulse, brightness.
Commands set via HTTP GET request with HTTP response JSON object.
This script handles setting the led using the library picozero.
The picozero LED class functions can be set via the POST request.
Reference: https://picozero.readthedocs.io/en/latest/recipes.html#leds
:commands (selective)
LED ON
curl -v -H "Content-Type: application/json" -d "{\"led\":\"red\",\"cmd\":\"on\",\"value\":0}" http://picow-ip
{"status": "OK", "title": {"led": "red", "value": 0, "cmd": "on"}, "message": "on"}
LED OFF
curl -v -H "Content-Type: application/json" -d "{\"led\":\"red\",\"cmd\":\"off\",\"value\":0}" http://picow-ip
{"status": "OK", "title": {"led": "red", "value": 0, "cmd": "off"}, "message": "off"}
LED Brightness
curl -v -H "Content-Type: application/json" -d "{\"led\":\"yellow\",\"cmd\":\"brightness\",\"value\":0.1}" http://picow-ip
{"status": "OK", "title": {"led": "yellow", "value": 0.1, "cmd": "brightness"}
:note
When using curl ensure to escape the " to \" in the JSON object.
:log
ledcontrol-device-change-httppost-brightness v20230409
Network connected OK
Network IP picow-ip
Network listening on ('0.0.0.0', 80)
Network client connected from client-ip
HTTP Command={'led': 'yellow', 'value': 0, 'cmd': 'on'}
HTTP Response={"status": "OK", "title": {"led": "yellow", "value": 0, "cmd": "on"}, "message": "on"}
Network connection closed
Network client connected from client-ip
HTTP Command={'led': 'yellow', 'value': 0.1, 'cmd': 'brightness'}
HTTP Response={"status": "OK", "title": {"led": "yellow", "value": 0.1, "cmd": "brightness"}, "message": "brightness"}
Network connection closed
Network client connected from client-ip
HTTP Command={'led': 'yellow', 'value': 0, 'cmd': 'off'}
HTTP Response={"status": "OK", "title": {"led": "yellow", "value": 0, "cmd": "off"}, "message": "off"}
Network connection closed
"""
# Libraries
from machine import Pin
import json
# Picozero - note: beta version
import picozero
from picozero import LED
# Import network class
from server import Server
# Configuration read from config.py (must be uploaded to the picow prior testing)
import config
# Constants
NAME = 'ledcontrol-device-change-httppost'
VERSION = 'v20230409'
# Create the 3 LED objects GP2,3,4
led_red = LED(2)
led_red.off()
led_yellow = LED(3)
led_yellow.off()
led_green = LED(4)
led_green.off()
"""
Control an LED.
:param object led
    LED object created via led = LED(GPIO pin number)
    
:param string cmd
    LED command, like on, off, toggle, blink, pulse, brightness
    
:param int|float|string value
    Value for the command, like for brightness a float between 0-1
"""
def set_led(led,cmd,value):
    # Set the command
    if cmd == 'on':
        led.on()
    elif cmd == 'off':
        led.off()
    elif cmd == 'toggle':
        led.toggle()
    elif cmd == 'blink':
        led.blink()
    elif cmd == 'pulse':
        led.pulse()
    elif cmd == 'brightness':
        if 0 <= value <= 1:
            led.brightness = value
        else:
            print(f'[ERROR] Command {cmd} value {value} out of range 0-1.')
    else:
        prinf('[ERROR] Command {cmd} unknown.')
"""
Handle the request containing the command as JSON object.
The LED is turned on or off depending JSON key state {"state":0 or 1}
The response JSON object is updated.
Reference: https://picozero.readthedocs.io/en/latest/recipes.html#leds
:param string data
    JSON object with key:value pair to set the LED
    led:red|green|yellow, cmd:on|off|blink<pulse|brightness, value:NNN
:return JSON object response
"""
def handle_request(data):
    # Get the JSON key: 
    led = data['led'].lower()
    cmd = data['cmd']
    value = data['value']
    if led == 'red':
        set_led(led_red,cmd,value)
    elif led == 'green':
        set_led(led_green,cmd,value)
    elif led == 'yellow':
        set_led(led_yellow,cmd,value)
    else:
        prinf('[ERROR] LED {led} unknown.')
        
    # Response is OK
    response[config.KEY_STATE] = config.STATE_OK
    response[config.KEY_MESSAGE] = cmd
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
