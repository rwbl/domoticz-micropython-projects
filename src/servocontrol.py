"""
File:	servocontrol.py
Date:	20230318
Author:	Robert W.B. Linn
PicoW RESTful webserver listening for data from Domoticz event.
The incoming data is from a HTTP POST request with JSON object to set the position (angle) of a servo motor 0-180 degrees.
:log
Domoticz Servo Control v20230311
Network connected OK
Network IP webserver-ip
Network listening on ('0.0.0.0', 80)
Network client connected from NNN.NNN.NNN.23
HTTP Command={'angle': 180}
Servo position deg=180,duty=500000
HTTP Response={"status": "OK", "title": {"angle": 180}, "message": "180"}
Network connection closed
:wiring
Servo = PicoW
VCC = VBUS (5V) (red)
Signal = GP0 (pin #1) (yellow)
GND = GND (black)
"""
# Libraries
import time
from time import sleep
from machine import Pin
import json
# Call server from server.py (must be uploaded to the picow)
from server import Server
# Servo lib stored in PicoW folder lib
from servo import Servo
# Configuration read from config.py (must be uploaded to the picow prior testing)
import config
# Constants
NAME = 'Domoticz Servo Control'
VERSION = 'v20230311'
# Create the LED1 (blue) object using config.py settings
led1 = Pin(2, Pin.OUT)
led1.off()
# Create the servo object with the default (GP0 (Pin #1)
servo = Servo()
# Set the servo pos and log
def set_servo_position(pos):
    duty = servo.set_angle(pos)
    print("Servo position deg=" + str(pos) + ",duty=" + str(duty))
"""
Handle the resquest to set the servo pos between 0-180 degrees.
"""
def handle_request(cmd, status):
    # Assign the command to the response title
    response[config.KEY_TITLE] = cmd
    # If the status is 1 (OK) then set the lcd display with the sensor data.
    if status == 1:
        led1.on()
        
        # Get the angle of the servo to set
        angle = cmd['angle']
        
        # Set the servo pos
        set_servo_position(angle)
        # Set the response
        response[config.KEY_STATE] = config.STATE_OK
        response[config.KEY_MESSAGE] = str(angle)
        led1.off()
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
        
