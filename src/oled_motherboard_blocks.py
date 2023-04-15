"""
File:	oled_motherboard_block.py
Date:	20230324
Author:	Robert W.B. Linn
:description
On 0,96inch I2C OLED display connected to the PicoW, display text and selective RPi motherboard sensor data received from Domoticz.
The PicoW runs a RESTful webserver handling incoming data from a Domoticz Automation event dzVents.
The incoming data is received from a HTTP POST request with JSON object to set the text.
The JSON object contains for each of the displayed sensor data the block number, title and value.
[{'block': 1, 'title': 'Time', 'value': '1403'}, {'block': 2, 'title': 'Temp', 'value': 42}, {'block': 3, 'title': 'CPU', 'value': 0.37}, {'block': 4, 'title': 'Mem', 'value': 22}, {'block': 5, 'title': 'ARM', 'value': 600}, {'block': 6, 'title': 'HDD', 'value': 39}]
This enables to set the OLED display layout from the Domoticz event.
:log
Domoticz Motherboard v20230323
Init OLED address=60, sda=GP0, scl=GP1
Network connected OK
Network IP picow-ip
Network listening on ('0.0.0.0', 80)
Network client connected from client-ip
HTTP Command=[{'block': 1, 'title': 'Time', 'value': '1405'}, {'block': 2, 'title': 'Temp', 'value': 42}, {'block': 3, 'title': 'CPU', 'value': 0.45}, {'block': 4, 'title': 'Mem', 'value': 22}, {'block': 5, 'title': 'ARM', 'value': 600}, {'block': 6, 'title': 'HDD', 'value': 39}]
HTTP Response={"status": "OK", "title": [{"block": 1, "title": "Time", "value": "1405"}, {"block": 2, "title": "Temp", "value": 42}, {"block": 3, "title": "CPU", "value": 0.45}, {"block": 4, "title": "Mem", "value": 22}, {"block": 5, "title": "ARM", "value": 600}, {"block": 6, "title": "HDD", "value": 39}], "message": ""}
Network connection closed
:wiring
OLED = PicoW
GND = GND
VCC = 3V3
SCL = GP1 (pin #2)
SDA = GP0 (pin #1)
"""
# Libraries
import time
from time import sleep
from machine import Pin, I2C
import json
# Call server from server.py (must be uploaded to the picow)
from server import Server
# OLED display lib stored in PicoW folder lib
import ssd1306ex
from ssd1306ex import SSD1306_I2C
# Configuration read from config.py (must be uploaded to the picow prior testing)
import config
# Constants
## Name (row 0), Version (row 1), Waiting (row 3) are displayed on the OLED
NAME	= 'Domoticz Motherboard'
VERSION = 'v20230324'
WAITING = 'Waiting for data...'
## Title used for the HTTP JSON response to Domoticz key title
TITLE 	= 'Set OLED'
def init_oled(pin_sda=ssd1306ex.PIN_SDA, pin_scl=ssd1306ex.PIN_SCL, width=ssd1306ex.DISPLAY_WIDTH, height=ssd1306ex.DISPLAY_HEIGHT):
    """
    Create the OLED object. The I2C 0 is used.
        
    :param int pin_sda
        
    :param int pin_scl
        
    :param int width
        Width of the display, default = 128
        
    :param int height
        Height of the display, default = 64
        
    :return
        OLED object
        
    :example
        init_oled()
    """
    try:
        # Init I2C
        i2c = I2C(0, sda=Pin(pin_sda), scl=Pin(pin_scl), freq=400000)
        
        # OLED display with 128px width and 64px height and i2C
        oled = SSD1306_I2C(width, height, i2c)
        print(f'Init OLED address={oled.addr}, sda=GP{pin_sda}, scl=GP{pin_scl}')
        # Return the OLED object
        return oled
    except OSError as e:
        raise RuntimeError('[ERROR] Init OLED: {e}.')
def handle_request(cmd, status):
    """
    Handle the OLED command defined as JSON object.
    The command defines for every sensor data the text and the OLED start position col/row.
    {'timestamp': {'text': 'RPi Info  10:52', 'col': 0, 'row': 0}, 'memoryusage': {'text': 'Mem:22%', 'col': 0, 'row': 3}, 'cpuusage': {'text': 'CPU:0.3%', 'col': 0, 'row': 2}, 'internaltemperature': {'text': 'Temp:44C', 'col': 0, 'row': 1}}
    :param JSON object
        JSON object with key:value pair {"state":"on" or "off"}
    :status
        If status is 1 set the display else unknown command
        
    :return JSON object response
    """
    # Assign the command to the response title
    response[config.KEY_TITLE] = cmd
    # If the status is 1 (OK) then set the OLED display with the sensor data.
    if status == 1:
        # Clear the display first
        oled.clear()
        sleep(.1)
        # Set the sensor data in the text blocks 1-6
        for item in cmd:
            oled.text_block(item['block'],item['title'],item['value'])
    
        # Show the text blocks
        oled.show()
        
        # Set the response
        response[config.KEY_STATE] = config.STATE_OK
        response[config.KEY_MESSAGE] = config.MESSAGE_EMPTY
    else:
        response[config.KEY_STATE] = config.STATE_ERR
        response[config.KEY_MESSAGE] = config.MESSAGE_CMD_UNKNOWN
    
    # Return the response which is send to Domoticz
    return response
print(f'{NAME} {VERSION}')
# Create the OLED display object
oled = init_oled(ssd1306ex.PIN_SDA, ssd1306ex.PIN_SCL, ssd1306ex.DISPLAY_WIDTH, ssd1306ex.DISPLAY_HEIGHT)
# Show initial info on the OLED. Waiting is replaced by RPi motherboard sensor data
oled.text_rows(NAME, VERSION, '', WAITING)
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
        # Get the cmd to set the OLED text as JSON object from the POST request
        cmd, status = network.parse_post_request(request)
        # Create the HTTP response JSON object
        response = {}
        
        # Handle the command to update the OLED text.
        # Set the response
        response = handle_request(cmd, status)
        
        # Send the response to Domoticz and close the connection (wait for new)
        network.send_response(cl, response, True)
    except OSError as e:
        ledstatus.off()
        cl.close()
        print('[ERROR] Network - Connection closed')
