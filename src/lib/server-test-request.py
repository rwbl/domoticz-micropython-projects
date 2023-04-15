"""
server-test-request.py
20230318 rwbl
PicoW RESTful webserver sending a HTTP API/JSON request to Domoticz.
:log
"""
# Libraries
import time
from machine import Pin
# Import server class from server.py
from server import Server
# Configuration read from config.py (must be uploaded to the picow prior testing)
import config
# Constants
NAME = 'LEDControl Network REQUEST'
VERSION = 'v20230318'
CRLF = chr(13) + chr(10)
SPACE = chr(32)
# URL params to switch LED1 on or off or request state
# http://pico-ip/command
URL_REQUEST = "http://"+config.DOMOTICZ_IP+"/json.htm?type=command&param=udevice&idx={IDX}&nvalue=0&svalue={SVALUE}"
IDX_DEVICE = 15
# Create the LED1 object using config.py settings
led1 = Pin(config.PIN_LED1, Pin.OUT)
led1.value(0)
"""
Main
"""
print(f'{NAME} {VERSION}')
# Create network object
network = Server(config.WIFI_SSID, config.WIFI_PASSWORD)
# Connect to the network and get the server object
server = network.connect()
while True:
    # Submit Domoticz HTTP API/JSON request to update the device
    url = URL_REQUEST
    url = url.replace('{IDX}', str(IDX_DEVICE))
    url = url.replace('{SVALUE}', '22;62;1')
    status, content = network.send_get_request(url)
    print(f'Response GET request status={status},json={content}')
    # Delay in seconds till next sample
    time.sleep(10)
