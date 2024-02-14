# domoticz-micropython-projects - TODO

## FIX: BLE OpenMQTTGateway Data Workaround
Find a way to read the environment data published instead the workaround using the name with data.
### Status
In progress.
Changed the OMG setting "pubadvdata" to true.
```
home/OpenMQTTGateway/commands/MQTTtoBT/config -m '{"pubadvdata":true}'
```
The OMG shows the manufacturer data:
```
{"id":"28:CD:C1:09:05:98","mac_type":0,"adv_type":0,"name":"04623904064B","manufacturerdata":"feff04623904064b","rssi":-55}
```
Workaround will be replaced by using the key manufacturerdata containing the manufacturer id + environment data.
See project BLE Actuators.

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
In progress using BLE communication (active mode).

## NEW: Optimize RAM usage for constants
See [MicroPython for Microcontrollers](https://docs.micropython.org/en/latest/reference/constrained.html).
### Status
Not started.

## NEW: Project LCD480x320 Touch Support
Enable touch support instead external pushbuttons.
Touch support requires high memory, which is limited on the Raspberry Pi Pico (264kB of SRAM, 2MB of on-board flash memory).
### Status
Wait for a new Raspberry Pi Pico with more memory or consider using an Olimex.
Not started.

## NEW: Project ESP32CYD
Many todos - see TODO.md in archive esp32cyd.zip (src folder).

Considering to develop this project as a dedicated github project **HomeControlPanel** and leave ESP32CYD as experimental.

The **HomeControlPanel** to be made flexible by enabling controlling other Home Automation systems.
### Status
In progress.


