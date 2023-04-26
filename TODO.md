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

## NEW: Smart Home IOT Model
Build a Smart Home IOT Model (SHIM) with various sensors&actuators controlled by Domoticz.
The SHIM will have at least 1 microcontroller Raspberry Pi Pico W acting as a web server & mqtt autodiscover client.
Additional microcontroller could be Raspberry Pi Pico connected to the Pico W.
Communication between SHIM and Domoticz via mqtt messaging with mqtt autodiscover topics.
The SHIM could be a LEGO house (from LEGO City) , wooden house, makerbeam frame or meccano frame.
### Status
Not started.
