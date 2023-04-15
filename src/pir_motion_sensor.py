"""
File:	pir-motion-detection.py
Date:	20230325
Author:	Robert W.B. Linn
:description
PicoW RESTful webserver listening if a motion is detected.
If a motion is detected, an HTTP API/JSON request is send to Domoticz to set an the Level and Text for an Alert Device.
Also a RED LED is blinking for a sec. In addition a GREEN LED is on every 5 seconds to indicate the motion detector is working.
Example: Motion detected sets alert level 4 with text "Motion detected".
:log
pir-motion-detection v20230326
Network connected OK
Network IP webserver-ip
Network listening on ('0.0.0.0', 80)
Motion detected!
Send GET request url=http://domoticz-ip:port/json.htm?type=command&param=udevice&idx=7&nvalue=4&svalue=Motion Detected
Send GET request status=OK
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
# Constants
NAME = 'pir-motion-detection'
VERSION = 'v20230326'
# Domoticz alert sensor
URL_DOM_ALERT_DEVICE = 'http://' + config.DOMOTICZ_IP + '/json.htm?type=command&param=udevice&idx={IDX}&nvalue={LEVEL}&svalue={TEXT}'
IDX_ALERT_DEVICE = 7
ALERT_LEVEL = 4
ALERT_TEXT = 'Motion Detected'
# Motion detection duration (red led blinking): 1s = 10 cycles a 100ms
MOTION_DETECTION_DURATION = 10
# Create LED objects
# LED RED GPIO2 indicated motion detected (blinking)
led_red = machine.Pin(2, machine.Pin.OUT)
led_red.value(0)
# LED GREEN GPIO4 indicates motion detection process running
led_green = machine.Pin(4, machine.Pin.OUT)
led_green.value(0)
# Set GPIO13 PIR_Interrupt as input
sensor_pir=Pin(13, Pin.IN, Pin.PULL_UP)
# Handle motion detection triggered by the interrupt
def pir_handler(pin):
    print("Motion detected!")
    url = URL_DOM_ALERT_DEVICE
    url = url.replace('{IDX}', str(IDX_ALERT_DEVICE))
    url = url.replace('{LEVEL}', str(ALERT_LEVEL))
    url = url.replace('{TEXT}', str(ALERT_TEXT))
    
    network.send_get_request(url)
    
    # Let red led blink for a sec
    for i in range(MOTION_DETECTION_DURATION): 
        led_red.toggle() 
        time.sleep_ms(100)
    led_red.value(0)
# Attach external interrupt to GPIO13 and rising edge as an external event source
sensor_pir.irq(trigger=machine.Pin.IRQ_RISING, handler=pir_handler)
"""
Handle Request
"""
def handle_request(cmd):
    print(f'NOT USED')
    
"""
Main
"""
print(f'{NAME} {VERSION}')
# Create network object
network = Server(config.WIFI_SSID, config.WIFI_PASSWORD)
# Connect to the network and get the server object
server = network.connect()
while True:
    led_green.toggle() 
    time.sleep(5)
