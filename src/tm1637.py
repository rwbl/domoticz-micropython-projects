"""
File:	tm1637.py
Date:	20230318
Author:	Robert W.B. Linn
:description
PicoW RESTful webserver listening for data from Domoticz event.
The incoming data is from a HTTP POST request with JSON object.
The JSON object has key:value pais: {"data":NNNN}
LED1 is attached on the Pico Breadboard kit.
:log
Domoticz TM1637 v20230304
TM1637 init.
Network connected OK
Network IP webserver-ip
Network listening on ('0.0.0.0', 80)
Network client connected from NNN.NNN.NNN.23
HTTP Command={'data': 40.90001}
HTTP Response={"title": {"data": 40.90001}, "message": "41°C", "status": "OK"}
Network connection closed
:wiring
TM1637 = PicoW
VCC	= VBUS (5V) (red)
DIO	= GP20 (pin #26) (white)
CLK = GP21 (pin #27) (pink)
GND = GND (black)
"""
# Libraries
import time
from time import sleep
from machine import Pin
# Call server from server.py (must be uploaded to the picow)
from server import Server
# TM1637 lib stored in PicoW folder lib
import tm1637
# Configuration read from config.py (must be uploaded to the picow prior testing)
import config
# Constants
NAME = 'Domoticz TM1637'
VERSION = 'v20230304'
# Create the LED1 (blue) object using config.py settings
led1 = Pin(config.PIN_LED1, Pin.OUT)
led1.off()
# LCD2004 Constants
TM1637_I2C_ADDRESS = 0x27
TM1637_PIN_DIO = 20
TM1637_PIN_CLK = 21
# Create the TM1637 object by init the TM1637 with i2c.
# Example: setTM1637(TM1637_I2C_ADDRESS, TM1637_PIN_DIO, TM1637_PIN_CLK)
# Return - TM1637 object
def init_tm1637(address, pindio, pinclk):
    try:
        # Init TM1637 object
        tm = tm1637.TM1637(clk=Pin(pinclk), dio=Pin(pindio))
        print("TM1637 init.")
        return tm
    except OSError as e:
        raise RuntimeError('[ERROR] TM1637 init.')
# TM1637 set display from the JSON object.
# cmd - Command from the key response[config.KEY_TITLE]
# Example: cmd['data']=41.3001
# Return - Temperature rounded
def set_tm1637(cmd, status):
    # Assign the command to the response title
    response[config.KEY_TITLE] = cmd
    # If the status is 1 (OK) then set the tm1637 with data.
    if status == 1:
        # Clear the display
        tm.show('    ')
        sleep(.3)
        # Get the temperature rounded (no digits) from the JSON key 'data'
        temperature = round(cmd['data'])
        # Set the display NN°C
        tm.temperature(temperature)
        # Not Used = Just to show
        # Set the display - number only, i.e. 41
        # tm.number(temperature)
        # Set the response
        # Convert the KEY_TITLE from JSON object to a string
        response[config.KEY_MESSAGE] = str(temperature) + "°C"
        response[config.KEY_STATE] = config.STATE_OK
    else:
        response[config.KEY_STATE] = config.STATE_ERR
        response[config.KEY_MESSAGE] = config.MESSAGE_CMD_UNKNOWN
        
    return response
# Main
# Listen for incoming connections from the Domoticz Automation Event dzVents
print(f'{NAME} {VERSION}')
# Set the TM1637 display
tm = init_tm1637(TM1637_I2C_ADDRESS, TM1637_PIN_DIO, TM1637_PIN_CLK)
tm.show('1958')
#tm.show('    ')
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
        
        # Set the display with data from the command
        response = set_tm1637(cmd, status)
        
        # Send the response to Domoticz and close the connection (wait for new)
        network.send_response(cl, response, True)
    except OSError as e:
        ledstatus.off()
        cl.close()
        print('[ERROR] Network Connection closed')
        
