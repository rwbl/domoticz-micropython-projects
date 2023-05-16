# domoticz-micropython-projects - TODO

## NEW: RF433
Send data to Domoticz RFXCom hardware device, via a cheap RF433 transmitter connected to a Pico W.
The data to be assigned to a Domoticz RFXMeter device. The message send by the RF433 transmitter is in X10 format.
### Status
Developed a MicroPython class pyRFXMeter with test script but the message is not recognized by the RFXTRX433e device.
The class is converted from Arduino CPP code and is running fine on an Arduino Nano.
Both MicroPython and CPP logs are the same i.e., same bits send for the messages.
Need to explore why the MicroPython script data send to the RFXCOM RFXtrx433e is not recognized.  
May a Pico frequency issue?

## NEW: Smart Home Mini Model
Build a Smart Home minI Model (SHIM) with various sensors & actuators controlled by Domoticz.
The SHIM will have at least 1 Raspberry Pi Pico W microcontroller acting as a web server & mqtt autodiscover client.
Additional microcontrollers could be a Raspberry Pi Pico connected to the Pico W.
Communication between SHIM and Domoticz via mqtt messaging with mqtt autodiscover topics.
The SHIM could be a LEGO house (from LEGO City) , wooden house, makerbeam frame or meccano frame.
THis project will also be used to learn how to create & maintain a single package with several classes to control SHIM.
### Status
Not started.

## NEW: Optimize RAM usage for constants
See [MicroPython for Microcontrollers](https://docs.micropython.org/en/latest/reference/constrained.html).
### Status
Not started.

## NEW: Raspberry Pi Debug Probe Device.
Check out the new Raspberry Pi Debug Probe Device.
### Status
Not started.

## NEW: MQTT-AD Domoticz Alert Sensor
Create and update a Domoticz Alert Sensor. Not supported at time of writing (20230515)
### Status
Not started.
