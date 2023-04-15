"""
File:   bmp280.py
Date:   20230327
Author: Robert W.B. Linn
:description
Read in regular intervals the BMP280 temperature and barometric pressure and update a Domoticz Temp+Baro device.
The Domoticz devices are updated using HTTP API/JSON POST request Custom Event to the Domoticz server.
:example
http://domoticz-ip:port/json.htm?type=command&param=udevice&idx=IDX&nvalue=0&svalue=TEMP;BAR;BAR_FOR;ALTITUDE
IDX = device id,TEMP = Temperature,BAR = Barometric pressure,BAR_FOR = Barometer forecast (see below),ALTITUDE = 0
Barometer forecast: 0 = Stable,1 = Sunny,2 = Cloudy,3 = Unstable,4 = Thunderstorm,5 = Unknown,6 = Cloudy/Rain
:notes
Pico Breadboard Kit is used to wire up the BMP280.
Pico Breadboard Kit LED1 is used as status LED when requesting BMP280 data and updating domoticz.
Configuration stored in config.py, ensure to upload to the picow.
BMP280 measures every 60 seconds.
:log
BMP280 v20230326
Sampling Rate: 60s.
Network connected OK
Network IP picow-ip
Network listening on ('0.0.0.0', 80)
BMP280 t=24,p=101340.5,hpa=1013,bar=1.013404,mmhg=760.1157,svalue=24;1013;0;0
Send GET request url=http://domoticz-ip:port/json.htm?type=command&param=udevice&idx=29&nvalue=0&svalue=24;1013;0;0
Send GET request status=OK
:wiring
BMP280 = PicoW
VCC (+) = 3V3 (Pin #36)
GND (-) = GND (Pin #28)
SDI     = GP0 (Pin #1)
SCK     = GP1 (Pin #2)
LED (green)	= PicoW
+ (Anode) = GP4 (pin #6)
GND (Cathode) = GND (Pin #38)
"""
# Imports
from machine import Pin,I2C
from utime import sleep
# BMP280
from bmp280 import *
# Call server from server.py (must be uploaded to the picow)
from server import Server
# Configuration (must be uploaded to the picow)
import config
# Constants
VERSION = 'BMP280 v20230326'
# Create the led object (GP4, Pin #6) indicating bmp280 measurement in progress
led_green = Pin(4, Pin.OUT)
led_green.value(0)
    
# BMP280 SCK & SDA Pins and address
BMP_PIN_SDI = 0
BMP_PIN_SCK = 1
BMP_ADDR = 0x77
# BMP280 measurement sampling rate in seconds
SAMPLING_RATE = 60
# BMP280 IDX of the Domoticz Temp+Baro device
IDX_TEMP_BARO = 29
# URL Domoticz
# Note the idx of the domoticz device ( see GUI > Setup > Devices)
# The svalue is added in the main loop after getting the data from the BMP280 module.
# The svalue format: TEMP;BAR;BAR_FOR;ALTITUDE
URL_DOM = "http://"+ config.DOMOTICZ_IP +"/json.htm?type=command&param=udevice&idx={IDX}&nvalue=0&svalue={SVALUE}"
# Create the bmp280 sensor object
# Init the bus with GP0 (SDA) and GP1 (CLK)
bus = I2C(0, scl=Pin(BMP_PIN_SCK), sda=Pin(BMP_PIN_SDI), freq=200000)
# Create the bmp280 object with address 0x77. The default address 0x76 gives error OSError: [Errno 5] EIO
bmp = BMP280(bus, addr=BMP_ADDR)
# The use case is indoor
bmp.use_case(BMP280_CASE_INDOOR)
"""
Set the barometer forecast depending pressure.
:param int pressure
:return int forecast
    0=Stable,1=Sunny,2=Cloudy,3=Unstable,4=Thunderstorm,5=Unknown,6=Cloudy/Rain
"""
def barometer_forecast(pressure):
    if pressure < 966:
        return 4	# THUNDERSTORM
    elif pressure < 993:
        return 2	# CLOUDY
    elif pressure < 1007:
        return 6	# PARTLYCLOUDY
    elif pressure < 1013:
        return 3	# UNSTABLE
    elif pressure < 1033:
        return 0	# STABLE
    else:
        return 5	# Unknown
"""
BMP280 measurement with rounded values for temperature and pressure.
During measurement, the green led is on.
:return string svalue
    svalue with TEMP;BAR;BAR_FOR;ALTITUDE
:example svalue
    19;1004;6;0
"""
def get_bmp280_data():
    led_green.value(1)
    sleep(1)
    # print(f'BMP280 measuring...')
    temperature	= round(bmp.temperature)
    pressure    = bmp.pressure
    p_pa		= pressure
    p_hpa		= round(pressure/100)
    p_bar		= pressure/100000
    p_mmHg		= pressure/133.3224
    forecast	= barometer_forecast(p_hpa)
    
    # Set the svalue, i.e. svalue=TEMP;BAR;BAR_FOR;ALTITUDE
    svalue = str(temperature) + ';' + str(p_hpa) + ';' + str(forecast) + ';' + str(0)
    print(f"BMP280 t={temperature},p={p_pa},hpa={p_hpa},bar={p_bar},mmhg={p_mmHg},svalue={svalue}")
    
    # Return the svalue
    led_green.value(0)
    return svalue
# Info
print(f'{VERSION}')
print(f'Sampling Rate: {SAMPLING_RATE}s.')
# Create network object
network = Server(config.WIFI_SSID, config.WIFI_PASSWORD, DEBUG=True)
# Connect to the network and get the server object
server = network.connect()
# Domoticz url
url = URL_DOM
url = url.replace('{IDX}', str(IDX_TEMP_BARO))
# Main
while True:
    # Measure & submit BMP280 data to Domoticz
    network.send_get_request(url = url.replace('{SVALUE}', get_bmp280_data()))
    # Delay till next sample
    sleep(SAMPLING_RATE)
