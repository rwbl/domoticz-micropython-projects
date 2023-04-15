"""
potmeterdimmer.py
20230330 rwbl
To dim a Domoticz dimmer switch.
The Domoticz device is updated using HTTP API/JSON request to the Domoticz server.
:notes
Pico Breadboard Kit is used to wire up the potmeter.
Configuration stored in config.py, ensure to upload to the picow.
:log
PotMeterDimmer v20230330
Network connected OK
Network IP webserver-ip
Network listening on ('0.0.0.0', 80)
value=11026, level=17, prev_level=-1, abs=18
Send GET request url=http://domoticz-ip:port/json.htm?type=command&param=switchlight&idx=1&switchcmd=Set%20Level&level=17
Send GET request status=OK
value=224, level=0, prev_level=17, abs=17
Send GET request url=http://domoticz-ip:port/json.htm?type=command&param=switchlight&idx=1&switchcmd=Set%20Level&level=0
Send GET request status=OK
:wiring
PotMeter = PicoW
VCC (+) = VBUS (Pin #40)
OUT = GP26 (Pin #31, ADC0)
GND (-) = GND (Pin #28)
LED = PicoW
+ (Anode) = GP16 (Pin #21)
"""
# Imports
from machine import Pin, ADC, PWM
from utime import sleep
# Call server from server.py (must be uploaded to the picow)
from server import Server
# Configuration (must be uploaded to the picow)
import config
# Constants
VERSION = 'PotMeterDimmer v20230330'
# Dimmer min max range using offsets
DIMMER_MAX = const(65500)	# 65535
DIMMER_MIN = const(250)		# 0
# Helper to map the PWM range to 0-100%
def mapRange(value, inMin, inMax, outMin, outMax):
    return outMin + (((value - inMin) / (inMax - inMin)) * (outMax - outMin))
# Create ADC0 object GP26
adc0 = ADC(0)
# Create PWM LED GP16 to control the dimmer level 0-100%
pwmled = PWM(Pin(16, Pin.OUT))
pwmled.freq(1000)
# IDX of the Domoticz Dimmer Switch device
IDX_DIMMER = 1
# URL Domoticz
# Note the idx of the domoticz device ( see GUI > Setup > Devices)
# /json.htm?type=command&param=switchlight&idx=99&switchcmd=Set%20Level&level=6
URL_DOM = 'http://'+config.DOMOTICZ_IP+'/json.htm?type=command&param=switchlight&idx='+str(IDX_DIMMER)+'&switchcmd=Set%20Level&level='
# Por meter noise level 2%
NOISE_LEVEL = 2
# Keep the previous level
prev_level = -1
"""
Get the dimmer level between 0-100.
:return int level
    level between 0-100
:example
    18
"""
def set_dimmer_level():
    global prev_level
    # Read ADC0
    # Noise reduction: Not used but either LSB divide (adc0.read_u16() >> 2) or remove (adc0.read_u16() & 0b1111111111111100)
    value = adc0.read_u16()
    
    # Map the potmeter range to 0-100
    level = round(mapRange(value, DIMMER_MIN, DIMMER_MAX, 0, 100))
    # Check if the abs value between the current and prev reading is greater noise level
    if abs(prev_level - level) > NOISE_LEVEL:
        print(f'value={value}, level={level}, prev_level={prev_level}, abs={abs(level - prev_level)}')
        # Set PWM-Duty-Cycle = brightness of the control LED
        pwmled.duty_u16(value)
        
        # Keep the prev level
        prev_level = level
        # Submit Domoticz HTTP API/JSON GET request to update the device
        network.send_get_request(URL_DOM + str(level))
        sleep(0.5)
    
# Info
print(f'{VERSION}')
# Create network object
network = Server(config.WIFI_SSID, config.WIFI_PASSWORD, DEBUG=True)
# Connect to the network and get the server object
server = network.connect()
# Main
while True:
    # Listen to potmeter changes & set domoticz dimmer to 0-100%
    set_dimmer_level()    
  
