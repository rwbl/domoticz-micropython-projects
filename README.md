# domoticz-micropython-projects

## Purpose
To explore how to use the MicroPython programming language running on embedded hardware interfacing with the Domoticz Home Automation System.

The core of the projects uses the Raspberry Pi Pico W microcontroller, with components like actuators & sensors.
The microcontroller is acting as a web server to communicate with the Domoticz Home Automation System.

The intention is to provide some practical guidance, inspire ideas .. but not to explain Domoticz nor programming languages.

## Prerequisites
It is expected to have basic knowledge of 
* Domoticz Home Automation System
* Domoticz Automation Event system dzVents & Lua
* Programming languages Python and MicroPython
* Raspberry Pi Pico / Pico W and ESP microcontrollers
* Thonny Integrated Development Environment
* JavaScript Object Notation (JSON)

## Remarks
* This is a working document = conceptual changes & new idea’s whilst progressing.
* There might be better solutions = changes depend on the author’s learning curve.
* To-Do actions are tagged with [TODO] and captured in the file TODO.md.
* Hard- and Software versions are subject to change.
* Drawings are created with Fritzing.
* Sources included in this document - latest sources this GitHub repository folder src.

## Concept
![image](https://user-images.githubusercontent.com/47274144/232204025-2bf210c4-1355-41b6-8fdf-85d3b7750874.png)

The block diagram starts at the left with the MicroPython editor (Thonny) running on the development device (Notebook with Windows 11).

Connected to the development device is a Microcontroller Unit (MCU) with external components (actuators & sensors).
For the Pico W projects, the Pico Breadboard Kit or the Pico IO Shield is used. These are a rather handy boards, not only for experimenting but also for building prototypes.

The MCU is running as a web server (programmed as a class in MicroPython) sending HTTP GET/POST requests to connected clients or receiving HTTP requests from connected clients.

The connected clients can be any client (like a Web Browser, Node-RED or Application), but for this book the client is a dedicated Domoticz Development System running on a Raspberry Pi 4B 4GB with Raspberry Pi OS version 11 (bullseye).

The Domoticz hardware and related devices are added depending on the requirements of the project as described in this book. Most of the devices are virtual sensors assigned to the Hardware Dummy.
Automation events are developed in dzVents (Domoticz Easy Events).
Event scripting with dzVents is well integrated in Domoticz and good documentation with loads of examples available.
The Domoticz editor (GUI > Setup > More Options > Events) is used to develop and test the scripts (My Automation Scripts).

In addition, Node-RED and MQTT broker mosquitto are running on the Raspberry Pi.

The software is regularly updated to stay at the latest versions – for Domoticz the release channel Beta 2023.1 (build 15092 or higher) is set (at the time of writing).

## Components
*	1x Raspberry Pi Pico W 2022.
*	1x Pico Breadboard Kit GeeekPi with LEDs (4 named LED1-4), Pushbuttons (4 named Button K1 - K4), Buzzer (not used for now).
*	1x Pico IO Shield KEYESTUDIO.
*	1x DHT22 - Temperature & Humidity sensor.
*	1x LCD 20x4 - LCD display (I2C) 20 columns & 4 rows.
*	1x TM1637 - 4-digit 7-segment LED display (I2C).
*	1x Servo Motor - Tower Pro Micro Servo 9g SG90.
*	1x RFID-RC522 – Reader for MIFARE RFID Cards and Tokens.
*	1x TM1638 LED&KEY - 8x 7-segment decimal LED component with 8x individual LEDs and 8x push buttons.
*	1x PIR Motion Sensor.
*	1x Potentiometer.
*	2x DS18B20 –  1-wire digital thermometers.
and more …

## Credits
**THANKS**, to the developers of the Raspberry Pi & ESP Microcontroller, Domoticz Home Automation System, MicroPython Language, Libraries & Tools and to all sharing related information. Without these, it would not be possible to write this document.

## Licence
GNU GENERAL PUBLIC LICENSE v3.0.
The information shared for personal use only - use at your own risk (see LICENSE).

