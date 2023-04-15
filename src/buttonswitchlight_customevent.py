"""
File:   buttonswitchlight_customevent.py
Date:   20230418
Author: Robert W.B. Linn
:description
Turn Domoticz Switch (IDX=16) On/Off by pressing Pico Breadboard Kit Button K4.
If the switch state is On, the Pico Breadboard Kit LED1 is On else Off.
The Domoticz switch device state is changed by using HTTP API/JSON POST request to the Domoticz server.
Example:
http://domoticz-ip:8080/json.htm?type=command&param=customevent&event=switchlight&data={"idx":16,"state":"On"}
http://domoticz-ip:8080/json.htm?type=command&param=customevent&event=switchlight&data={"idx":16,"state":"Off"}
:notes
This script handles button press using the library picozero.
Configuration is stored in config.py - Ensure to upload to the picow.
The button K4 of the Pico Breadboard Kit is used.
Press the button short set the switch state On or Off.
When keeping the button down the switch state with change On/Off constantly.
:log
ButtonSwitchLight Custom Event v20230410
Network connected OK
Network IP picow-ip
Network listening on ('0.0.0.0', 80)
Button K4 pressed - setstatus=On
Send POST request url=http://domoticz-ip:port/json.htm?type=command&param=customevent&event=switchlight&data=, postdata={'idx': 16, 'state': 'On'}
Send POST request status=OK
Button K4 pressed - setstatus=Off
Send POST request url=http://domoticz-ip:port/json.htm?type=command&param=customevent&event=switchlight&data=, postdata={'idx': 16, 'state': 'Off'}
Send POST request status=OK
:wiring
Pico Breadboard Kit Button = PicoW
K4 = GP20 (Pin #26)		# Pushbutton
LED1 = GP16 (Pin #21)	# LED switch state
The PicoW onboard LED is also used to indicate the network connection state.
"""
# Convert the Domoticz HTTP API/JSON response
import json
from machine import Pin, Timer
from utime import sleep
# picozero - BETA version - beginner-friendly library to help you use common electronics components with the Raspberry Pi Pico. Thanks to Raspberry Pi Foundation.
from picozero import Button
# Network class to communicate with Domoticz or other clients
from server import Server
# Configuration (must be uploaded to the picow)
import config
# Constants
NAME = 'ButtonSwitchLight Custom Event'
VERSION = 'v20230410'
# Create the led object indicating the state of the K4 button On/Off
ledbuttonstatus = Pin(config.PIN_LED1, Pin.OUT)
ledbuttonstatus.value(0)
# Button K4 pin
BUTTON_PINNR = 20
# Button K4 object
btn = Button(BUTTON_PINNR)
switch_status = "Off"
## Domoticz IDX of the Switch device
IDX_SWITCH = 16
# URL Domoticz
# Note the idx of the domoticz device ( see GUI > Setup > Devices)
# http://domoticz-ip:port/json.htm?type=command&param=customevent&event=MyEvent&data=MyData
URL_DOM_SWITCH = "http://"+ config.DOMOTICZ_IP +"/json.htm?type=command&param=customevent&event=switchlight&data="
   
# Handle Key Pressed
def set_domoticz_switch():
    global switch_status
    if switch_status == "Off":
        switch_status = "On"
        ledbuttonstatus.value(1)
    else:
        switch_status = "Off"
        ledbuttonstatus.value(0)
    print(f'Button K4 pressed - setstatus={switch_status}')
    # Post data
    postdata = {}
    postdata['idx'] = 16
    postdata['state'] = switch_status
    # Submit domoticz
    status = network.send_post_request(URL_DOM_SWITCH, postdata)
# Main
print(f'{NAME} {VERSION}')
# Create network object
network = Server(config.WIFI_SSID, config.WIFI_PASSWORD)
# Connect to the network and get the server object
server = network.connect()
"""
Press the button short set the switch state On or Off.
When keeping the button down the switch state with change On/Off constantly.
"""
while True:
    # Check if the button is pressed
    if btn.is_pressed:
        # If the button is not released then set the switch state
        if btn.is_released == False:
            set_domoticz_switch()
