"""
File:	config.py
Date:	20230425
Author:	Robert W.B. Linn
:description
Constants for the MCU webserver.
Specific constants for the Pico Breadboard Kit.
Import the configuration file: import config.py
Access an configuration item: config.PIN_LED1
"""
# Import the const package
from micropython import const
# Network
# WIFI_SSID       = const('SSID')
# WIFI_PASSWORD   = const('password')
# Domoticz IP + Port
DOMOTICZ_IP		= const('domoticz-ip:port')
# Pico W onboard LED
PIN_LED_ONBOARD = const('LED')
# Pico Breadboard Kit LEDs connected to GPnn (pin #nn)
PIN_LED1		= const(16)	#Pin 21
PIN_LED2		= const(17)	#Pin 22
PIN_LED3		= const(18)	#Pin 24
PIN_LED4		= const(19)	#Pin 25
# Pico Breadboard Kit Buttons connected to GPnn (pin #nn)
PIN_BUTTON_K1	= const(20)	#Pin 26
# Domoticz
# HTTP response JSON keys
KEY_STATE		= const('status')
KEY_TITLE		= const('title')
KEY_MESSAGE		= const('message')
# Messages used for HTTP response
STATE_OK			= const('OK')
STATE_WARNING		= const('WARNING')
STATE_ERR			= const('ERROR')
MESSAGE_EMPTY		= const('')
MESSAGE_UNKNOWN		= const('Unknown')
MESSAGE_CMD_UNKNOWN	= const('Unknown command.')
MESSAGE_ON			= const('On')
MESSAGE_OFF			= const('Off')
