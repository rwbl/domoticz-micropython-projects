"""
File:	lcdmotherboard.py
Date:	20230318
Author:	Robert W.B. Linn
On an LCD2004 connected to the PicoW, display text and selective RPi motherboard sensor data received from Domoticz.
The PicoW runs a RESTful webserver handling incoming data from a Domoticz Automation event dzVents.
The incoming data is received from a HTTP POST request with JSON object to set the text.
The JSON object contains for each of the displayed text, the col, row and text.
{'sensor': {'text': 'TEXT', 'col': NN, 'row': N}, ...}
This enables to set the LCD display layout from the Domoticz event.
:log
Domoticz Motherboard v20230311
LCD init. Address: [39]
Network connected OK
Network IP webserver-ip
Network listening on ('0.0.0.0', 80)
Network client connected from NNN.NNN.NNN.23
HTTP Command={'timestamp': {'text': '16:00', 'col': 15, 'row': 1}, 'memoryusage': {'text': 'M:20', 'col': 14, 'row': 3}, 'cpuusage': {'text': 'C:0.3', 'col': 6, 'row': 3}, 'internaltemperature': {'text': 'T:41', 'col': 0, 'row': 3}}
HTTP Response={"status": "OK", "title": {"timestamp": {"text": "16:00", "col": 15, "row": 1}, "memoryusage": {"text": "M:20", "col": 14, "row": 3}, "cpuusage": {"text": "C:0.3", "col": 6, "row": 3}, "internaltemperature": {"text": "T:41", "col": 0, "row": 3}}, "message": ""}
Network connection closed
:wiring
LCD2004 = PicoW
VCC = VBUS (5V) (red)
SDA = GP20 (pin #26) (white)
SCL = GP21 (pin #27) (pink)
GND = GND (black)
"""
# Libraries
import time
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
## Name (row 0), Version (row 1), Waiting (row 3) are displayed on the LCD
NAME = 'Domoticz Motherboard'
VERSION = 'v20230311'
WAITING = 'Waiting for data...'
## Title used for the HTTP JSON response to Domoticz key title
TITLE = 'Set LCD'
# Create the LED1 (blue) object using config.py settings
led1 = Pin(config.PIN_LED1, Pin.OUT)
led1.off()
# LCD2004 Constants
LCD_I2C_ADDRESS = 0x27
LCD_PIN_SDA = 20
LCD_PIN_SCL = 21
LCD_ROWS = 4
LCD_COLS = 20
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
init_lcd(LCD_I2C_ADDRESS, LCD_PIN_SDA, LCD_PIN_SCL, LCD_ROWS, LCD_COLS)
"""
def init_lcd(address, pinsda, pinscl, rows, cols):
    try:
        # I2C object
        i2c = I2C(0, sda=Pin(pinsda), scl=Pin(pinscl), freq=100000)
        # Init LCD object using I2C with address & rows (4, index 0-3) & cols (20, index 0-19)
        lcd = I2cLcd(i2c, address, rows, cols)
        print("LCD init. Address: " + str(i2c.scan()))
        return lcd
    except OSError as e:
        raise RuntimeError('[ERROR] LCD init.')
"""
LCD Initial text on row 1 & 2
"""
def set_lcd_welcome(row1, row2, row3, row4):
    lcd.putstr(row1 + "\n" + row2 + "\n" + row3 + "\n" + row4)
    sleep(.3)
"""
Set the sensor text at col, row
:param string Sensor
    String defining the RPi motherboard sensor, i.e. internaltemperature
:example
set_lcd_sensor_text('internaltemperature')
"""
def set_lcd_sensor_text(data, sensor):
    # Get the sensor data
    col = data[sensor]['col']
    row = data[sensor]['row']
    text = data[sensor]['text']
    # Clear the sensor data text at col, row
    lcd.clrtext(col, row, len(text))
    sleep(.1)
    # Write the sensor text at col, row
    lcd.putstrat(col, row, text)
    sleep(.1)
"""
Handle the LCD command defined as JSON object.
The command defines for every sensor data the text and the LCD start position col/row.
{'timestamp': {'text': '15:53', 'col': 15, 'row': 1}, 'memoryusage': {'text': 'M:20', 'col': 14, 'row': 3}, 'cpuusage': {'text': 'C:0.39', 'col': 6, 'row': 3}, 'internaltemperature': {'text': 'T:39', 'col': 0, 'row': 3}}
:param JSON object
    JSON object with key:value pair {"state":"on" or "off"}
:status
    If status is 1 set the display else unknown command
    
:return JSON object response
"""
def handle_request(cmd, status):
    # Assign the command to the response title
    response[config.KEY_TITLE] = cmd
    # If the status is 1 (OK) then set the lcd display with the sensor data.
    if status == 1:
        # Clear rows first (the row range for LCD2004 is 0 to 3)
        # Clear row 2 = NOT USED
        lcd.clrrow(2)
        sleep(.1)
        
        # Row 3 is used to display the RPi motherboard sensor data
        lcd.clrrow(3)
        sleep(.1)
        # Set the sensor data (subset only) on row 3
        set_lcd_sensor_text(cmd, 'timestamp')
        set_lcd_sensor_text(cmd, 'internaltemperature')
        set_lcd_sensor_text(cmd, 'cpuusage')
        set_lcd_sensor_text(cmd, 'memoryusage')
        # Set the response
        response[config.KEY_STATE] = config.STATE_OK
        response[config.KEY_MESSAGE] = config.MESSAGE_EMPTY
    else:
        response[config.KEY_STATE] = config.STATE_ERR
        response[config.KEY_MESSAGE] = config.MESSAGE_CMD_UNKNOWN
    
    # Return the response which is send to Domoticz
    return response
# Main
# Listen for incoming connections from the Domoticz Automation Event dzVents
print(f'{NAME} {VERSION}')
# Create the LCD display object
lcd = init_lcd(LCD_I2C_ADDRESS, LCD_PIN_SDA, LCD_PIN_SCL, LCD_ROWS, LCD_COLS)
# Show initial info on the LCD. Waiting is replaced by RPi motherboard sensor data
set_lcd_welcome(NAME, VERSION, '', WAITING)
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
        
        # Handle the command to update the LCD text.
        # Set the response
        response = handle_request(cmd, status)
        
        # Send the response to Domoticz and close the connection (wait for new)
        network.send_response(cl, response, True)
    except OSError as e:
        ledstatus.off()
        cl.close()
        print('[ERROR] Network - Connection closed')
