# domoticz-micropython-projects - TODO

## NEW: UltraSonic Sensor
Measure distance with the HCSR04.
### Status
Not started.

## NEW: IKEA Vindriktning
Measure air quality with the IKEA Vindriktning sensor.
### Status
Not started.

## NEW: RF433
Send data to Domoticz RFXCom hardware device, via a cheap RF433 transmitter connected to a Pico W.
The data to be assigned to a Domoticz RFXMeter device. The message send by the RF433 transmitter is in X10 format.
### Status
Developed a MicroPython class pyRFXMeter with test script but the message is not recognized by the RFXTRX433e device.
The class is converted from Arduino CPP code running fine on an Aduino Nano.
Both MicroPython and CPP logs are the same, i.e. same bits send for the messages.
Need to explore why the MicroPython code is not running on the Pico W? May a Pico frequency issue. No idea?

## NEW: Explore MQTT Auto Discovery
MicroPython MQTT client on the embedded hardware which can publish discovery messages for the connected component(s) and subscribes to associated Domoticz device(s) messages.
See Domoticz forum [post](https://www.domoticz.com/forum/viewtopic.php?p=302037#p302037).
### Status
Started to explore using a DHT22 temperature sensor connected to a Raspberry Pi Pico W.
See Domoticz forum [post](https://www.domoticz.com/forum/viewtopic.php?f=82&t=40249).

## UPD: Network Connection
Connecting the Pico W first time, it (sometimes) takes more then 5 tries to get a network connection.
Explore why.
### Status
Not started.

## UPD: Improve Network Errors
Example: URL incorrect.
b'<html><head><title>Not Found</title></head><body><h1>404 Not Found</h1></body></html>'
### Status
Not started.
