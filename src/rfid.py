"""
File:	rfid.py
Date:	20230319
Author:	Robert W.B. Linn
:description
Read the UID of an RFID card and send to Domoticz text device.
The Domoticz text device is updated using HTTP API/JSON request to the Domoticz server.
The log of the Domoticz text device lists all the cards read.
The time between the card readings must be greater threshold to avoid multiple readings and updates of the Domoticz text device.
The threshold in seconds is defined as constant MIN_DELTA_TIME = 2.
:notes
Pico Breadboard Kit is used to wire up the RFID.
Pico Breadboard Kit LED1 is used as status LED when requesting RFID data and updating domoticz.
Configuration stored in config.py, ensure to upload to the picow.
For a later version, its planned to send the RFID card data, beside the RFID card UID. This could be done via custom event.
:credits
The MFRC522 library PiPicoRFID from Saket Upadhyay (https://github.com/Saket-Upadhyay/PiPicoRFID).
The base code is from https://github.com/wendlers/micropython-mfrc522.
:log
RFID v20230319
Network connected OK
Network IP webserver-ip
Network listening on ('0.0.0.0', 80)
Init RFID Module=rp2
CARD DETECTED: tag_type=10, uid_hex=346FC2CF, uid_dec=879739599
Send GET request url=http://domoticz-ip:8080/json.htm?type=command&param=udevice&idx=27&nvalue=0&svalue=879739599
Send GET request status=OK
CARD DETECTED: tag_type=10, uid_hex=56381D00, uid_dec=1446518016
Send GET request url=http://domoticz-ip:8080/json.htm?type=command&param=udevice&idx=27&nvalue=0&svalue=1446518016
Send GET request status=OK
:wiring
RFID-RC522 Module = Pico W
VCC = 3.3V
RST = GP0
GND = GND
IRQ = Not connected
MISO = GP4
MOSI = GP3
SCK = GP2
SDA = GP1
"""
"""
Imports
"""
from machine import Pin
from utime import sleep
import time
# RFID
import mfrc522
from os import uname
# Call server from server.py (must be uploaded to the picow)
from server import Server
# Configuration (must be uploaded to the picow)
import config
# Constants
VERSION = 'RFID v20230319'
# Create the led object indicating RFID read in progress
led1 = Pin(config.PIN_LED1, Pin.OUT)
led1.value(0)
"""
Domoticz
"""
# IDX text device
IDX_RFID = 27
# URL to update the text device
# Note the idx of the domoticz device ( see GUI > Setup > Devices)
# The svalue is added in the main loop after getting the data from the RFID.
URL_DOM = "http://"+ config.DOMOTICZ_IP +"/json.htm?type=command&param=udevice&idx=" + str(IDX_RFID) + "&nvalue=0&svalue="
"""
RFID
"""
# Flag to read the data
# Not used as only the card uid is used
READ_DATA = False
"""
RFID Timer
"""
first_time_reading = True
# Delta time between readings in seconds
MIN_DELTA_TIME = 2
# Start time in seconds
start_time = time.time()
# Read_time
read_time = start_time
# Previous UID NOT USED
uid_previous = -1
"""
RFID object init
:return object mfrc522
"""
def init_rfid():
    print(f'Init RFID Module={str(uname()[0])}')
    return mfrc522.MFRC522(sck=2, miso=4, mosi=3, cs=1, rst=0)
    # print(f'Place card before reader. READ ARRD: 0x08')
"""
Read the RFID data (optional)
:param object rdr
    Card reader object
    
:return string hexstr
    Card data as hex string
    
:example
read_data(rdr)
RAW DATA: ['0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0']
['0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0']
"""
def read_data(rdr):
    hexstr = []
    # Get the card data (optional)
    if rdr.select_tag(raw_uid) == rdr.OK:
        key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        auth = rdr.auth(rdr.AUTHENT1A, 8, key, raw_uid)
        if rdr.auth(rdr.AUTHENT1A, 8, key, raw_uid) == rdr.OK:
            data = rdr.read(8)
            # print(data) [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            if data is not None:
                for i in data:
                    hexstr.append(hex(i))
            print("RAW DATA: " + str(hexstr))
            rdr.stop_crypto1()
        else:
            print("AUTH ERR")
    else:
        print("Failed to select tag")
    return hexstr
"""
Main
"""
print(f'{VERSION}')
# Create network object
network = Server(config.WIFI_SSID, config.WIFI_PASSWORD, DEBUG=True)
# Connect to the network and get the server object
server = network.connect()
# Init the RFID module
rdr = init_rfid()
while True:
    # Wait for RFID card to read.
    # If RFID card found, send the card UID as decimal to Domoticz text device
    # Read the rfid card data
    (stat, tag_type) = rdr.request(rdr.REQIDL)
    # print(stat)
    # If the reader status is OK, then get the card type and uid
    if stat == rdr.OK:
        # LED1 indicator on
        led1.value(1)
        # Get the reading status and uid as raw data
        (stat, raw_uid) = rdr.anticoll()
        # If the status is OK, lets send the UID to Domoticz
        if stat == rdr.OK:
            # Get the tag type, i.e. 10
            tagtype = f'{tag_type:0X}'
            # Get the card uid as hex (each byte 2 hex size in uppercase) and dec, i.e. 56381D00 = 1446518016
            # The dec value is send to domoticz
            uid_hex = f'{raw_uid[0]:0>2X}{raw_uid[1]:0>2X}{raw_uid[2]:0>2X}{raw_uid[3]:0>2X}'
            uid_dec = int(uid_hex, 16)
            print(f'CARD DETECTED: tag_type={tagtype}, uid_hex={uid_hex}, uid_dec={uid_dec}')
            # Read_time and check the delta time in seconds between the readings
            # This to avoid multiple text device updates within (milli)seconds
            read_time = time.time()
            delta_time = read_time - start_time
            # print(f'{start_time}, {read_time}, {delta_time}')
            # Update domoticz if the delta time exceeded or if first time reading
            if delta_time > MIN_DELTA_TIME or first_time_reading:
                first_time_reading = False
                uid_previous = uid_dec
                start_time = read_time
                
                # Submit Domoticz HTTP API/JSON GET request to update the device
                # The uid card id decimal value is submitted to the Domoticz text device
                network.send_get_request(URL_DOM + str(uid_dec))
                
                # Read data is not used and to be developed further like handling auth error
                if READ_DATA:
                    data = read_data(rdr)
                    # network.send_get_request(URL_DOM + data)
        
        # LED1 indicator off
        led1.value(0)
