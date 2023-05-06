"""
File:	steppermotorled.py
Date:	20230505
Author:	Robert W.B. Linn
:description
PicoW RESTful webserver to move a stepper motor (28BYJ-48 Stepper Motor with ULN2003 motor driver).
The incoming data is from a HTTP POST request with JSON object (key:value pair) containing the command tp control the stepper motor:
angle: NNN
steps: NNN
rotate: NNN
LED indicators
After successful LAN connection, the green led is on.
Whilst handling a stepper motor control request, the red led is on end the green led is off.
:examples
Command submitted using curl with HTTP response.
curl -v -H "Content-Type:application/json" -d "{\"angle\":90}" http://picow-ip
{"title": "{'angle': 90}", "message": "90", "status": "OK"}
curl -v -H "Content-Type:application/json" -d "{\"angle\":-90}" http://picow-ip
{"title": "{'angle': -90}", "message": "-90", "status": "OK"}
curl -v -H "Content-Type:application/json" -d "{\"steps\":-200}" http://picow-ip
{"status": "OK", "title": "{'steps': -200}", "message": "-200"}
curl -v -H "Content-Type:application/json" -d "{\"rotate\":2}" http://picow-ip
{"status": "OK", "title": "{'rotate': 2}", "message": "2"}
curl -v -H "Content-Type:application/json" -d "{\"rotate\":-2}" http://picow-ip
{"status": "OK", "title": "{'rotate': -2}", "message": "-2"}
Error example:
curl -v -H "Content-Type:application/json" -d "{\"step\":100}" http://picow-ip
{"status": "ERROR", "title": "{'step': 100}", "message": "Unknown command."}
:references
https://docs.micropython.org/en/latest/library/uasyncio.html
:log
Stepper Motor v20230505
Network waiting for connection...
Network connected OK
Network IP picow-ip
Network listening on ('0.0.0.0', 80)
Network client connected from client-ip
HTTP Command={'steps': -200}
HTTP Response={"status": "OK", "title": "{'steps': -200}", "message": "-200"}
Network connection closed
Network client connected from client-ip
HTTP Command={'step': 100}
HTTP Response={"status": "ERROR", "title": "{'step': 100}", "message": "Unknown command."}
Network connection closed
Network client connected from client-ip
HTTP Command={'steps': -200}
HTTP Response={"status": "OK", "title": "{'steps': -200}", "message": "-200"}
Network connection closed
Network client connected from client-ip
HTTP Command={'rotate': 2}
HTTP Response={"status": "OK", "title": "{'rotate': 2}", "message": "2"}
Network connection closed
Network client connected from client-ip
HTTP Command={'rotate': -2}
HTTP Response={"status": "OK", "title": "{'rotate': -2}", "message": "-2"}
Network connection closed
:wiring
Stepper Motor = Pico W
IN1 = GP2
IN2 = GP3
IN3 = GP4
IN4 = GP5
VCC = External 5V 
GND = GND common with external GND
LED RED = Pico W
+ = GP21 (Pin #27)
GND = GND (Pin #28)
LED GREEN = Pico W
+ = GP20 (Pin #26)
GND = GND (Pin #28)
"""
# Libraries
# Steppermotor lib created by the author
from machine import Pin
from time import sleep
import json
# Call server from server.py (must be uploaded to the picow)
from server import Server
# Stepper stored in PicoW folder lib
# Credits: This library is based on: https://github.com/IDWizard/uln2003 (c) IDWizard 2017, # MIT License.
from stepper import Stepper
# Configuration read from config.py (must be uploaded to the picow prior testing)
import config
# Constants
NAME = 'Stepper Motor LED'
VERSION = 'v20230505'
# Create LED Objects
ledred = Pin(21, Pin.OUT)
ledred.off()
ledgreen = Pin(20, Pin.OUT)
ledgreen.off()
# Create a stepper motor object with defaults
stepper = Stepper()
"""
Handle the request to move the stepper.
"""
def handle_request(cmd, status):
    ledred.on()
    ledgreen.off()
    # Assign the command to the response title
    response[config.KEY_TITLE] = str(cmd)
    # Set the response initially to ok
    response[config.KEY_STATE] = config.STATE_OK
    # If the status is 1 (OK) then action
    if status == 1:
        
        # Get the command by checking the json key 
        if cmd.get('angle') != None:
            # Get the angle of the stepper to move
            angle = cmd['angle']            
            # Move the stepper by angle
            stepper.angle(angle)
            response[config.KEY_MESSAGE] = str(angle)
        elif cmd.get('steps') != None:
            # Get the number of steps for the stepper to move
            steps = cmd['steps']            
            # Move the stepper by steps
            stepper.step(steps)
            response[config.KEY_MESSAGE] = str(steps)
        elif cmd.get('rotate') != None:
            # Get the number of steps for the stepper to move
            ntimes = cmd['rotate']
            # Move the stepper by rotation
            stepper.rotate(ntimes)
            response[config.KEY_MESSAGE] = str(ntimes)
        else:
            response[config.KEY_STATE] = config.STATE_ERR
            response[config.KEY_MESSAGE] = config.MESSAGE_CMD_UNKNOWN
            
    else:
        response[config.KEY_STATE] = config.STATE_ERR
        response[config.KEY_MESSAGE] = config.MESSAGE_CMD_UNKNOWN
    
    ledred.off()
    ledgreen.on()
    # Return the response which is send to Domoticz
    return response
# Main
print(f'{NAME} {VERSION}')
# Create network object
network = Server(config.WIFI_SSID, config.WIFI_PASSWORD, DEBUG=True)
# Connect to the network and get the server object
server = network.connect()
ledgreen.on()
"""
Main Loop
"""
while True:
    try:
        # Get client connection and the request data
        cl, request = network.get_client_connection(server)
        # Get the cmd to set the LCD text as JSON object from the POST request
        cmd, status = network.parse_post_request(request)
        # Create the HTTP response JSON object
        response = {}
        
        # Handle the command to set the servo pos
        # Set the response
        response = handle_request(cmd, status)
        
        # Send the response to Domoticz and close the connection (wait for new)
        network.send_response(cl, response, True)
    except OSError as e:
        ledstatus.off()
        cl.close()
        print('[ERROR] Network Connection closed')
 
