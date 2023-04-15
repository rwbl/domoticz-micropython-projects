"""
File:	lcdledcontrol.py
Date:	20230318
Author:	Robert W.B. Linn
PicoW RESTful webserver listening for data from Domoticz event.
The incoming data is from a HTTP POST request with JSON object to switch LED1 on or off.
LED1 is attached on the Pico Breadboard kit.
:log
Example turning LED1 on from Domoticz:
HTTP Command:	{'state': 'on'}
HTTP Response:	{"status": "OK", "title": {"state": "on"}, "message": "On"}
:wiring
LCD2004 = PicoW
VCC = VBUS (5V) (red)
SDA = GP20 (pin #26) (white)
SCL = GP21 (pin #27) (pink)
GND = GND (black)
"""
# Libraries
from time import sleep
from machine import Pin
import json
# Call server from server.py (must be uploaded to the picow)
from server import Server
# LCD Display libs stored in PicoW folder lib
# lcd_api.py, machine_i2c_lcd.py
from machine import I2C, Pin
from machine_i2c_lcd import I2cLcd
# Configuration read from config.py (must be uploaded to the picow prior testing)
import config
# Constants
NAME = 'Domoticz LED Control'
VERSION = 'v20230311'
CRLF = chr(13) + chr(10)
SPACE = chr(32)
# Create the LED1 (blue) object using config.py settings
led1 = Pin(config.PIN_LED1, Pin.OUT)
led1.off()
# LCD2004 Constants
LCD_I2C_ADDRESS = 0x27
LCD_PIN_SDA = 20
LCD_PIN_SCL = 21
LCD_ROWS = 4
LCD_COLS = 20
def set_lcd(address, pinsda, pinscl, rows, cols):
    """
    Create the LCD object by init the lcd with i2c.
    :param hex address
        Address of the LCD I2C. Default 0x27
        
    :param int pinsda
        SDA pin
        
    :param int pinscl
        SCL pin
        
    :param int rows
        Number of rows 20 or 16
        
    :param int cols
        Number of cols 4 or 2
        
    :return
        LCD object
        
    :example
    set_lcd(LCD_I2C_ADDRESS, LCD_PIN_SDA, LCD_PIN_SCL, LCD_ROWS, LCD_COLS)
    """
    try:
        # I2C object
        i2c = I2C(0, sda=Pin(pinsda), scl=Pin(pinscl), freq=100000)
        # Init LCD object using I2C with address & rows (4, index 0-3) & cols (20, index 0-19)
        lcd = I2cLcd(i2c, address, rows, cols)
        print("LCD init. Address: " + str(i2c.scan()))
        return lcd
    except OSError as e:
        raise RuntimeError('[ERROR] LCD init.')
def set_lcd_welcome(row1, row2):
    """
    LCD Initial text on row 1 & 2
    """
    lcd.putstr(row1 + "\n" + row2)
    sleep(.3)
def handle_request(cmd, status):
    """
    Handle the LCD command defined as JSON object.
    :param JSON object
        JSON object with key:value pair {"state":"on" or "off"}
    :status
        If status is 1 set the display else unknown command
        
    :return JSON object response
    """
    # Assign the command to the response title
    response[config.KEY_TITLE] = cmd
    if status == 1:
        # Select the command and set the lcd text
        if cmd['state'] == 'on':
            led1.on()
            response[config.KEY_MESSAGE] = config.MESSAGE_ON
            response[config.KEY_STATE] = config.STATE_OK
        elif cmd['state'] == 'off':
            led1.off()
            response[config.KEY_MESSAGE] = config.MESSAGE_OFF
            response[config.KEY_STATE] = config.STATE_OK
        else:
            response[config.KEY_STATE] = config.STATE_ERR
            response[config.KEY_MESSAGE] = config.MESSAGE_CMD_UNKNOWN
    else:
            response[config.KEY_STATE] = config.STATE_ERR
            response[config.KEY_MESSAGE] = config.MESSAGE_CMD_UNKNOWN
        
    # LCD display set
    # Clear row 2 (the row range for LCD2004 is 0 to 3)
    lcd.clrrow(2)
    sleep(.3)
    # Write the keys message and state as string at col 0, row 2
    lcd.putstrat(0, 2, 'LED1: ' + response[config.KEY_MESSAGE] + ' ' + response[config.KEY_STATE])
    sleep(.3)
    return response
# Main
# Listen for incoming connections from the Domoticz Automation Event dzVents
print(f'{NAME} {VERSION}')
# Create the LCD object
lcd = set_lcd(LCD_I2C_ADDRESS, LCD_PIN_SDA, LCD_PIN_SCL, LCD_ROWS, LCD_COLS)
# Set the LCD display welcome text
set_lcd_welcome(NAME, VERSION)
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
        # Get the cmd as JSON object from the POST request
        # {"state":"on" or "off"}
        cmd, status = network.parse_post_request(request)
        # Create the HTTP response JSON object
        response = {}
        
        # Handle the command to update the LCD text.
        # Set the response
        response = handle_request(cmd, status)
        
        # Send the response to Domoticz and close the connection (wait for new)
        network.send_response(cl, response, True)
    except OSError as e:
        ledstatus.off()
        cl.close()
        print('[ERROR] Network Connection closed')
        
