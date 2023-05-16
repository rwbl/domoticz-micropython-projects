"""
File:	ikeavindriktning.py
Date:	20230515
Author: Robert W.B. Linn
:description
Library for the IKEA Vindriktning Air Quality sensor.
Tested on a Raspberry Pi Pico W.
:description
Receive data via UART Serial Communication from the IKEA Vindriktning Air Quality sensor based on particles.
PM2.5 = Particulate Matter 2.5µm Concentration (µg/m3), sensor PM1006.
The sensor sends every ~20 seconds, 5-6 messages which are received over the serial line UART0.
The message buffer received from the sensor must have a length of 20 bytes.
The bytes 5 & 6 are used to calculate the PM2.5 concentration.
An offset is used to update the sensor data in domoticz instead of updating with a value that has not changed.
(not used in this example).
:notes
The modification doesn't interfere with normal operation of the device in any way.
The Pico W just adds another data sink beside the colored LEDs.
:data example
b'\x16\x11\x0b\x00\x00\x006\x00\x00\x03`\x00\x00\x02Q\x02\x00\x00\xde\x02'
:wiring
IKEA Vindriktning = Pico W
VCC = 5V (Pin #40)
GND = GND (Pin #38)
Data = GP17 (Pin #22)
:usage
iv = IKEAVINDRIKTNING(0, 17, 5)
while True:
    if iv.uart.any():
        data = iv.get_data(iv.uart.read())
        if data != None:
            print(f'PM2.5 value={data[0]} ug/m3, level={data[1]}')
        time.sleep(1)
"""
__version__	= '0.5.0'
__author__	= 'Robert W.B. Linn'
__license__	= 'GNU GENERAL PUBLIC LICENSE Version 3, https://www.gnu.org/licenses/'
# Imports
from machine import Pin,UART
import time
 
# 
class IKEAVINDRIKTNING:
    # Define the air quality level thresholds min & max
    AIR_QUALITY_LEVEL_GREEN_MIN		= 0
    AIR_QUALITY_LEVEL_GREEN_MAX		= 35
    AIR_QUALITY_LEVEL_YELLOW_MIN	= AIR_QUALITY_LEVEL_GREEN_MAX
    AIR_QUALITY_LEVEL_YELLOW_MAX	= 85
    AIR_QUALITY_LEVEL_RED_MIN		= AIR_QUALITY_LEVEL_YELLOW_MAX
    AIR_QUALITY_LEVEL_RED_MAX		= 1000
    def __init__(self, uartport=0, rxpin=17, offset=5):
        """
        Init the class with default UART port and RX pin.
        
        :param int uartport
            Set the UART peripherals 0 (for UART0) or 1 (for UART1).
            
        :param int rxpin
            Set the receiver (RX pin). Default GP 17 (Pin #22).
        :param int offset
            Set the value offset used to transmit the data.
        """
        
        # Properties for the current & previous air quality & level
        self.air_quality_current = -1
        self.air_quality_previous = self.air_quality_current
        self.air_quality_level_current = -1
        self.air_quality_level_previous = self.air_quality_level_current
        self.air_quality_offset = offset
        # Create the uart instance with uart0, tx=None, rx=gp17
        self.uart = UART(uartport, baudrate=9600, tx=None, rx=Pin(rxpin))
        # Initialize the uart instance with 8 bits of data, no parity bit, and 2 stop bits.
        self.uart.init(bits=8, parity=None, stop=2)
    def is_valid_message_length(self, data):
        """Check if the message has 20 bytes"""
        if len(data) == 20:
            # print(f'Received message with correct length: {len(data)}.')
            return True
        else:
            print(f'[ERROR] Received message with invalid length: {len(data)}')
    def is_valid_message_header(self, data):
        """'Check the message header. The first 3 bytes must be 16 11 0B."""
        if (data[0] == 0x16) and (data[1] == 0x11) and (data[2] == 0x0B):
            # print(f'Received message with correct header.')
            return True
        else:
            print(f'[ERROR] Received message with invalid header.')
            return False
    def checksum(self, data):
        """Create a checksum."""
        return b'%02X' % (sum(data) & 0xFF)
    def is_valid_checksum(self, data):
        """Check if the data checksum is 0."""
        checksum = int(self.checksum(data))
        if (checksum == 0):
            # print(f'Received message with correct checksum: {checksum}.')
            return True
        else:
            print(f'[ERROR] Received message with invalid checksum. Expected: 0. Actual: {checksum}')
            return False
    def air_quality(self, data):
        """Calculate the air quality pm2.5 value from the bytes data 5 & 6"""
        air_quality = data[5] * 256 + data[6]
        # print(f'air_quality={air_quality}')
        return air_quality
    def air_quality_level(self, data):
        """
        Get the air quality level depending air_quality PM2.5 value.
        The sensor has 3 levels and LED indicators:
        Green LOW: 0-35=Good, Amber MEDIUM: 36-85=OK, Red (HIGH): 86-1000=NOT GOOD.
        Returns - air_quality level 1 = LOW (GREEN), 2 = MEDIUM (YELLOW), 3 = HIGH (RED)
        """
        # Set initial air quality level
        air_quality_level = -1
    
        # Get the air quality
        value = self.air_quality(data)        
        
        # Calculate the air quality level
        # Level 1 = LOW = GREEN
        if value <= self.AIR_QUALITY_LEVEL_GREEN_MAX:
            air_quality_level = 1
        # Level 2 = MEDIUM = YELLOW
        elif value > self.AIR_QUALITY_LEVEL_YELLOW_MIN and value <= self.AIR_QUALITY_LEVEL_YELLOW_MAX:
            air_quality_level = 2
        # Level 3 = HIGH = RED
        elif value > self.AIR_QUALITY_LEVEL_RED_MIN:
            air_quality_level = 3
        # print(f'air_quality_level={level}, value={value}')
        return air_quality_level
    def air_quality_data(self, data):
        """Get the sensor air_quality pm2.5 value 0-100 ug/m3 and the level 1-3 (GREEN, YELLOW, RED)."""
        # print(f'{data}')
        # Check the message data
        if self.is_valid_message_length(data) and self.is_valid_message_header(data) and self.is_valid_checksum(data):
            # Get the current air quality pm2.5 (0 - 100) and the level 1-3
            self.air_quality_current		= self.air_quality(data)
            self.air_quality_level_current	= self.air_quality_level(data)
            
            # Check if value has changed > offset (to avoid sending same values)
            if abs(self.air_quality_current - self.air_quality_previous) > self.air_quality_offset:
                self.air_quality_previous = self.air_quality_current
                self.air_quality_level_previous = self.air_quality_level_current
                # Log the data
                # print(f'PM2.5 value={self.pm_2_5_value_current} ug/m3, level={self.pm_2_5_level_current}')
                
                # Return dit with two entries
                return self.air_quality_current, self.air_quality_level_current
"""
TEST
iv = IKEAVINDRIKTNING(0, 17, 5)
while True:
    # Check if there is data received over the serial line.
    if iv.uart.any():
        # print(time.ticks_ms())
        data = iv.get_data(iv.uart.read())
        if data != None:
            print(f'PM2.5 value={data[0]} ug/m3, level={data[1]}')
        # Short delay
        time.sleep(1)
"""
