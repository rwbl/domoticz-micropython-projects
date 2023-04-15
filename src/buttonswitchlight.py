"""
File:   buttonswitchlight.py
Date:   20230418
Author: Robert W.B. Linn
:description
Turn Domoticz Switch (IDX=16) On/Off by pressing Pico Breadboard Kit Button K4.
If the switch state is On, the Pico Breadboard Kit LED1 is On else Off.
The Domoticz switch device state is changed by using HTTP API/JSON GET request to the Domoticz server.
http://domoticz-ip:port/json.htm?type=command&param=switchlight&idx=16&switchcmd=On or Off
:notes
This script handles button press using the library picozero.
Configuration is stored in config.py - Ensure to upload to the picow.
The button K4 of the Pico Breadboard Kit is used.
Press the button short set the switch state On or Off.
When keeping the button down the switch state with change On/Off constantly.
Instead of using the global switch_status could use the state of LED1 to determine if the light is on or off.
:log
ButtonSwitchLight v20230410
Network connected OK
Network IP picow-ip
Network listening on ('0.0.0.0', 80)
Button K4 pressed - setstatus=On
Send GET request url=http://domoticz-ip:port/json.htm?type=command&param=switchlight&idx=16&switchcmd=On
Send GET request status=OK
:wiring
Pico Breadboard Kit Button = PicoW
K4 = GP20 (Pin #26)		# Pushbutton
LED1 = GP16 (Pin #21)	# LED switch state
The PicoW onboard LED is also used	to indicate the network connection state.
"""
from machine import Pin, Timer
from utime import sleep
# picozero - BETA version
from picozero import Button
# Network class to communicate with Domoticz or other clients
from server import Server
# Configuration (must be uploaded to the picow)
import config
# Constants
NAME = 'ButtonSwitchLight'
VERSION = 'v20230410'
# Breadboard Kit LED1 object using config.py settings
led1 = Pin(config.PIN_LED1, Pin.OUT)
led1.value(0)
# LED object indicating the state of the K4 button On/Off
ledbuttonstatus = Pin(config.PIN_LED1, Pin.OUT)
ledbuttonstatus.value(0)
# Button K4 pin
BUTTON_PINNR = 20
# Button K4 object
btn = Button(BUTTON_PINNR)
# Status of the switch On or Off
switch_status = "Off"
# Domoticz IDX of the switch device
IDX_SWITCH = 16
# URL Domoticz
# Note the idx of the domoticz device ( see GUI > Setup > Devices)
# http://domoticz-ip:port/json.htm?type=command&param=switchlight&idx=99&switchcmd=<On|Off|Toggle|Stop>
# OK: {"status": "OK","title": "SwitchLight"}
# ERROR: {"message" : "Error sending switch command, check device/hardware (idx=nnn) !","status" : "ERROR","title" : "SwitchLight"}
URL_DOM_SWITCH = "http://"+config.DOMOTICZ_IP+"/json.htm?type=command&param=switchlight&idx=" + str(IDX_SWITCH) + "&switchcmd="
   
"""
Handle Button Pressed.
The global switch_status is used, but could also use the LED1 state.
"""
def set_domoticz_switch():
    global switch_status
    if switch_status == "Off":
        switch_status = "On"
        ledbuttonstatus.value(1)
    else:
        switch_status = "Off"
        ledbuttonstatus.value(0)
    print(f'Button K4 pressed - setstatus={switch_status}')
    # Submit HTTP API/JSON request to Domoticz to set switch status
    status = network.send_get_request(URL_DOM_SWITCH + switch_status)
"""
Main
"""
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
