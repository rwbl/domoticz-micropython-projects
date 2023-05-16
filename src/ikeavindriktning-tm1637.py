"""
File:	ikeavindriktning-tm1637.py
Date:	20230516
Author: Robert W.B. Linn
:description
Receive data via UART Serial Communication from the IKEA VINDRIKTNING Air Quality sensor based on particles.
PM2.5 = Particulate Matter 2.5µm Concentration (µg/m3).
The air quality value 0-100+ and the air quality level 1 (good), 2 (moderate), 3 (bad) are calculated.
The value is sent via HTTP API/JSON to a Domoticz Custom Sensor.
The value and level are displayed on a 7-segment-LED display.
This example is an enhancement of ikeavindriktning.py.
:wiring
IKEA VINDRIKTNING = Pico W
VCC = 5V (Pin #40, VBUS)
GND = GND (Pin #38)
Data = GP17 (Pin #22, UART0 RX) + Voltage divider 5V to 3V3
TM1637 I2C = Pico W
VCC	= VBUS (5V) (Pin #40)
SDA	= GP20 (Pin #26)
SCL	= GP21 (Pin #27)
GND = GND  (Pin #38)
"""
# Imports
from machine import Pin,UART
from utime import sleep
# Class IKEAVINDRIKTNING from the library ikeavindriktning.py - stored in Pico W folder lib
from ikeavindriktning import IKEAVINDRIKTNING
# TM1637 lib - stored in Pico W folder lib
import tm1637
# Class server from the library server.py  - stored in Pico W folder lib
from server import Server
# Configuration (must be uploaded to the picow)
import config
# Constants
VERSION = 'IKEA VINDRIKTNING TM1637 v20230516'
"""
PICO W
"""
PIN_UART0_RX = 17   # IKEA VINDRIKTNING UART0 RX Pin GP17 #Pin 22
"""
IKEA VINDRIKTNING SENSOR
"""
UART_BUS = 0        # UART bus 0
VALUE_OFFSET = 2    # Update Domoticz air quality device is abs value between old and new value > offset
# Create an IKEA VINDRIKTNING object
# UART Serial Bus Number 0 or 1, RX pin (default GP17), offset new/old value
iv = IKEAVINDRIKTNING(UART_BUS, PIN_UART0_RX, VALUE_OFFSET)
"""
TM1637
"""
TM1637_I2C_ADDRESS = 0x27	# Default I2C address
TM1637_PIN_DIO = 20
TM1637_PIN_CLK = 21
def tm1637_init(address, pindio, pinclk):
    """Create the TM1637 object by init the TM1637 with i2c.
        Example: tm1637_init(TM1637_I2C_ADDRESS, TM1637_PIN_DIO, TM1637_PIN_CLK)
        Return - TM1637 object
    """
    try:
        tm = tm1637.TM1637(clk=Pin(pinclk), dio=Pin(pindio))
        # print("TM1637 init.")
        return tm
    except OSError as e:
        raise RuntimeError('[ERROR] TM1637 init.')
def tm1637_set_display(value, level):
    """Display air quality value and level."""
    
    # Clear the display first
    tm.show('    ')
    sleep(.3)
    # Round the value
    value = round(value, 0)
    # Check if the value is < 100
    if value > 99:
        value = 99
    # Set the space between value and level
    space = ' '
    if value < 10:
        space = '  '
    # Set the text
    text = f'{value}{space}{level}'
    # Show the text
    tm.show(text)
"""
DOMOTICZ
"""
# IDX of the Domoticz Custom Sensor for the Air Quality
DOM_IDX = 46
# Domoticz API/JSON URL
# The svalue (containing the air quality) is added in the main loop after getting the data from the sensor.
DOM_URL = "http://"+ config.DOMOTICZ_IP +"/json.htm?type=command&param=udevice&idx=" + str(DOM_IDX) + "&nvalue=0&svalue="
# Info
print(f'{VERSION}')
# TM1637 display init
tm = tm1637_init(TM1637_I2C_ADDRESS, TM1637_PIN_DIO, TM1637_PIN_CLK)
tm.show(' Ok ')
# Create network object
network = Server(config.WIFI_SSID, config.WIFI_PASSWORD, DEBUG=True)
# Connect to the network and get the server object
server = network.connect2()
# Loop forever
while True:
    
    # Check if there is data send from the sensor via serial line
    if iv.uart.any():
        # Get the air quality & air quality level as dict
        data = iv.air_quality_data(iv.uart.read())
        
        # Check if the dict contains data - only if above offset 
        if data != None:
            # Log the air quality & level from the data dict
            print(f'Air Quality pm2.5={data[0]} ug/m3, level={data[1]}')
            # Display air quality value 0-99 and level 1-3 on the TM1637 display.
            tm1637_set_display(data[0], data[1])
    
            # Submit Domoticz HTTP API/JSON GET request to update the device
            network.send_get_request(DOM_URL + str(data[0]))
        # Wait a second
        sleep(1)
