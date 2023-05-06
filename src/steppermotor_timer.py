"""
File:	steppermotor_timer.py
Date:	20230506
Author:	Robert W.B. Linn
:description
PicoW RESTful webserver to move a stepper motor (28BYJ-48 Stepper Motor with ULN2003 motor driver).
The incoming data is from a HTTP POST request with JSON object (key:value pair) containing the command:
{"command":"run", "direction":1 or -1}.
The direction clockwise is 1 and anti-clockwise is -1.
{"command":"stop"}
The motor is running using a timer with periodic=10ms and callback which sets one step. The stepper motor object uses 1ms for a step.
Additionally a RED LED indicates if the stepper motor is running
:note
Prior using the timer class, explored other libraries like asyncio or thread ... but found (for now) too complex to use.
MicroPython’s Timer class defines a baseline operation of executing a callback with a given period (or once after some delay),
:examples
Command submitted using curl with HTTP response.
curl -v -H "Content-Type:application/json" -d "{\"command\":\"run\", \"direction\":1}" http://webserver-ip
{"status": "OK", "title": "{'command': 'run', 'direction': 1}", "message": "run"}
curl -v -H "Content-Type:application/json" -d "{\"command\":\"run\", \"direction\":-1}" http://webserver-ip
{"status": "OK", "title": "{'command': 'run', 'direction': -1}", "message": "run"}
curl -v -H "Content-Type:application/json" -d "{\"command\":\"stop\"}" http://webserver-ip
{"status": "OK", "title": "{'command': 'stop'}", "message": "stop"}
:log
Stepper Motor Timer v20230506
Network waiting for connection...
Network connected OK
Network IP picow-ip
Network listening on ('0.0.0.0', 80)
Network client connected from client-ip
Stepper Motor Command: run
HTTP Response={"status": "OK", "title": "{'command': 'run', 'direction': -1}", "message": "run"}
Network connection closed
Network client connected from client-ip
HTTP Command={'command': 'run', 'direction': 1}
HTTP Response={"status": "OK", "title": "{'command': 'run', 'direction': 1}", "message": "run"}
Network connection closed
Network client connected from client-ip
HTTP Command={'command': 'stop'}
HTTP Response={"status": "OK", "title": "{'command': 'stop'}", "message": "stop"}
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
GND = GND
"""
# Libraries
# Steppermotor lib created by the author
from machine import Pin
from machine import Timer
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
NAME = 'Stepper Motor Timer'
VERSION = 'v20230506'
# Create the LED1 (blue) object using config.py settings
led1 = Pin(21, Pin.OUT)
led1.off()
# Create a stepper motor object with defaults
stepper = Stepper()
sleep(0.1)
# Create the timer object used by the function handle_request
timer_stepper = Timer()
"""
Run the stepper motor by moving a single step in direction clockwise (cw) or anti-clockwise (acw).
Function is used by the timer_stepper object as callback.
Argument t is mandatory.
"""
def run_stepper_motor_cw(t):
    stepper.step(1)
def run_stepper_motor_acw(t):
    stepper.step(-1)
"""
Handle the request to move the stepper.
"""
def handle_request(cmd, status):
    # Assign the command to the response title
    response[config.KEY_TITLE] = str(cmd)
    # Set the response initially to ok
    response[config.KEY_STATE] = config.STATE_OK
    # If the status is 1 (OK) then action
    if status == 1:
        
        if cmd.get('command') != None:
            command = cmd['command']
            # print(f'Stepper Motor Command: {command}')
            if command == 'run':
                # Set the direction clockwise or anti-clockwise
                direction = 1
                if cmd.get('direction') != None:
                    direction = cmd['direction']
                # periodic with 10ms period
                if direction == 1:
                    timer_stepper.init(mode=Timer.PERIODIC, period=10, callback=run_stepper_motor_cw)
                elif direction == -1:
                    timer_stepper.init(mode=Timer.PERIODIC, period=10, callback=run_stepper_motor_acw)
                else:
                    print(f'[ERROR] Wrong direction')
                led1.on()
                response[config.KEY_MESSAGE] = 'run'
            elif command == 'stop':
                timer_stepper.deinit()
                led1.off()
                response[config.KEY_MESSAGE] = 'stop'
            else:
                response[config.KEY_STATE] = config.STATE_ERR
                response[config.KEY_MESSAGE] = config.MESSAGE_CMD_UNKNOWN
        else:
            response[config.KEY_STATE] = config.STATE_ERR
            response[config.KEY_MESSAGE] = config.MESSAGE_CMD_UNKNOWN
    else:
        response[config.KEY_STATE] = config.STATE_ERR
        response[config.KEY_MESSAGE] = config.MESSAGE_CMD_UNKNOWN
    # Return the response which is send to Domoticz
    return response
# Main
print(f'{NAME} {VERSION}')
# Create network object
network = Server(config.WIFI_SSID, config.WIFI_PASSWORD, DEBUG=True)
# Connect to the network and get the server object
server = network.connect()
"""
Main Loop
"""
while True:
    try:
        # Get client connection and the request data
        cl, request = network.get_client_connection(server)
        # Get the cmd
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
# start the asyncio program
# asyncio.run(main())
