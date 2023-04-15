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
Explore why?

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
