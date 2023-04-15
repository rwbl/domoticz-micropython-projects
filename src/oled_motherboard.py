"""
File:	oled_motherboard.py
Date:	20230323
Author:	Robert W.B. Linn
:description
On 0,96inch I2C OLED display connected to the PicoW, display text and selective RPi motherboard sensor data received from Domoticz.
The PicoW runs a RESTful webserver handling incoming data from a Domoticz Automation event dzVents.
The incoming data is received from a HTTP POST request with JSON object to set the text.
The JSON object contains for each of the displayed text, col and row.
{'sensor': {'text': 'TEXT', 'col': NN, 'row': N}, ...}
This enables to set the OLED display layout from the Domoticz event.
:log
Domoticz Motherboard v20230323
Init OLED address=60, sda=GP0, scl=GP1
Network connected OK
Network IP picow-ip
Network listening on ('0.0.0.0', 80)
Network client connected from client-ip
HTTP Command={'timestamp': {'text': 'RPi Info  10:52', 'col': 0, 'row': 0}, 'memoryusage': {'text': 'Mem:22%', 'col': 0, 'row': 3}, 'cpuusage': {'text': 'CPU:0.3%', 'col': 0, 'row': 2}, 'internaltemperature': {'text': 'Temp:44C', 'col': 0, 'row': 1}}
HTTP Response={"status": "OK", "title": {"timestamp": {"text": "RPi Info  10:52", "col": 0, "row": 0}, "memoryusage": {"text": "Mem:22%", "col": 0, "row": 3}, "cpuusage": {"text": "CPU:0.3%", "col": 0, "row": 2}, "internaltemperature": {"text": "Temp:44C", "col": 0, "row": 1}}, "message": ""}
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
VERSION = 'v20230323'
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
def set_oled_welcome(row1, row2, row3, row4):
    """
    Initial text at col 0 on row 1 to 4.
    """
    oled.text_col_row(row1, 0, 0)
    oled.text_col_row(row2, 0, 1)
    oled.text_col_row(row3, 0, 2)
    oled.text_col_row(row4, 0, 3)
    oled.show()
def set_oled_sensor_text(data, sensor):
    """
    Set the sensor text at col, row
    : param JSON data
        JSON object with keys for col, row and text.
        
    :param string Sensor
        String defining the RPi motherboard sensor, i.e. internaltemperature.
    :example
        set_oled_sensor_text('internaltemperature')
    """
    # Get the sensor data
    col = data[sensor]['col']
    row = data[sensor]['row']
    text = data[sensor]['text']
    oled.text_col_row(text, col, row)
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
        # Set the sensor data (subset only)
        set_oled_sensor_text(cmd, 'timestamp')
        set_oled_sensor_text(cmd, 'internaltemperature')
        set_oled_sensor_text(cmd, 'cpuusage')
        set_oled_sensor_text(cmd, 'memoryusage')
        # Show the text
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
set_oled_welcome(NAME, VERSION, '', WAITING)
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
