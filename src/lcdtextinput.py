"""
File:	lcdtextinput.py
Date:	20230425
Author:	Robert W.B. Linn
PicoW RESTful webserver listening for data from Domoticz event.
The data contains up-to 4 lines of text to set the LCD display 20x4.
The lines are separated by , from the text key of the post data.
"text": "Line1,Line2,Line3,Line4"
:log
NOTE: The log contains some warning for testing
LCD Widget Input Control v20230425
LCD init. Address: [39]
Network waiting for connection...
Network connected OK
Network IP picow-ip
Network listening on ('0.0.0.0', 80)
Network client connected from client-ip
HTTP Command={'text': '012345678901234567890,Line2,,Line4,Line5'}
[WARNING] Line 0 exceeds max length 20 (21).
[WARNING] Line 4 ("Line5") out of range 0-3.
HTTP Response={"title": {"text": "012345678901234567890,Line2,,Line4,Line5"}, "message": "[WARNING] Line 4 (\"Line5\") out of range 0-4.", "status": "WARNING"}
Network connection closed
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
NAME = 'LCD Text Input'
VERSION = 'v20230425'
CRLF = chr(13) + chr(10)
SPACE = chr(32)
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
        JSON object with key:value pair {"text":"widget_input"}
    :status
        If status is 1 set the display else unknown command
        
    :return JSON object response
    """
    # print(lcd.num_lines, lcd.num_columns)
    
    # Assign the command to the response title
    response[config.KEY_TITLE] = cmd
    # Reset the message
    response[config.KEY_MESSAGE] = ''
    # Rest response
    response[config.KEY_STATE] = config.STATE_OK
    # If the status is 1 set the LCD text else error
    if status == 1:
        # Clear the LCD first
        lcd.clear()
        # Write the text input from the widget starting at col 0, row 0
        # Get the text
        text = cmd['text']
        # Split the text by , into up-to 4 lines 0-3
        lines = text.split(",")
        linenr = 0
        # Loop over the lines and write the line at col 0, row rownr
        # Check if the number of lines and number of columns are in range
        for line in lines:
            if 0 <= linenr <= lcd.num_lines - 1:
                if len(line) > lcd.num_columns:
                    response[config.KEY_MESSAGE] = f'[WARNING] Line {linenr} exceeds max length {str(lcd.num_columns)} ({str(len(line))}).'
                    response[config.KEY_STATE] = config.STATE_WARNING
                    print(response[config.KEY_MESSAGE])
                    line = line[0:lcd.num_columns]
                lcd.putstrat(0, linenr, line)
                linenr = linenr + 1
            else:
                response[config.KEY_MESSAGE] = f'[WARNING] Line {linenr} ("{line}") out of range 0-{lcd.num_lines - 1}.'
                response[config.KEY_STATE] = config.STATE_WARNING
                print(response[config.KEY_MESSAGE])
        # sleep(.3)
    else:
        response[config.KEY_MESSAGE] = config.MESSAGE_CMD_UNKNOWN
        response[config.KEY_STATE] = config.STATE_ERR
        
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
        
