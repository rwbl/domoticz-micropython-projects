# domoticz-micropython-projects

## Purpose
To explore how to use the MicroPython programming language running on embedded hardware interfacing with the Domoticz Home Automation System.

The core of the projects uses the Raspberry Pi Pico W microcontroller (some using the ESP32), with components like actuators & sensors.
The microcontroller is acting as a web server or MQTT Auto Discovery client or BLE advertiser communicating with the Domoticz Home Automation System.

The intention is to provide some practical guidance, inspire ideas, but not to explain Domoticz nor programming languages.
... and to have fun experimenting ...

## Prerequisites
It is expected to have basic knowledge of
* Domoticz Home Automation System.
* Domoticz Automation Event system dzVents & Lua.
* Programming languages Python and MicroPython.
* Raspberry Pi Pico / Pico W and ESP8266/ESP32 microcontrollers.
* Thonny Integrated Development Environment.
* JavaScript Object Notation (JSON).
* Message Queuing Telemetry Transport MQTT and MQTT Auto Discovery.
* Bluetooth Low Energy (BLE).
* Node-RED Low-code programming for event-driven applications.

## Remarks
* This is a working document = conceptual changes & new idea’s whilst progressing.
* There might be better solutions = changes depend on the author’s learning curve.
* To-Do actions are tagged with [TODO].
* Hard- and Software versions are subject to change.
* Drawings are created with Fritzing.
* Sources included in this document - latest sources this GitHub repository folder _src_.

## Concept
![image](https://github.com/rwbl/domoticz-micropython-projects/assets/47274144/54f97a7f-8c10-4699-bb8d-e1994dc028cf)
The block diagram starts at the left with the MicroPython editor (Thonny) running on the development device (Notebook with Windows 11).

Connected to the development device is a Microcontroller Unit (MCU) with external components (actuators & sensors).
For the Pico W projects, the Pico Breadboard Kit or the Pico IO Shield is used. These are a rather handy boards, not only for experimenting but also for building prototypes.

The MCU communicates with the Domoticz Test System via HTTP, Bluetooth Low Energy (BLE) or MQTT.
The MCU acts as a
* Web Server by sending HTTP GET/POST requests to connected clients or receiving HTTP GET/POST requests from connected clients,
* MQTT Auto Discovery Client by publishing device configuration or state messages and subscribing to state messages,
* Bluetooth Low Energy (BLE) advertiser by sending messages to an OpenMQTTGateway, which publishes MQTT messages being converted by Node-RED flow to Domoticz MQTT Auto Discovery Message.

The connected clients can be any client (like a Web Browser, Node-RED or Application), but for this book the client is a dedicated Domoticz Test System running on a Raspberry Pi 4B 4GB with Raspberry Pi OS version 12 (bookworm).

The Domoticz hardware and related devices are added, either manually via the “Dummy Hardware Controller” or automatic via the “MQTT Auto Discovery Client Gateway with LAN interface” depending on the requirements of the project as described in this book.
Note
Whilst starting to write this book, most of the devices are virtual sensors assigned to the Dummy Hardware Controller, but also gradually start to use the (new) MQTT Auto Discovery feature.

The Automation events are developed in dzVents (Domoticz Easy Events).
Event scripting with dzVents is well integrated in Domoticz and good documentation with many examples is available.
The Domoticz editor (GUI > Setup > More Options > Events) is used to develop and test the scripts (My Automation Scripts).

In addition, Node-RED and MQTT broker mosquitto (with clients mosquitto_pub and mosquitto_sub) are running on the Raspberry Pi.

The software is regularly updated to stay at the latest versions – for Domoticz the release channel Beta 2024.3 (build 15866) is used (at the time of writing).

## Components
* 1x Raspberry Pi Pico W 2022.
* 1x Pico Breadboard Kit GeeekPi with LEDs (LED1-4), Pushbuttons (Button K1 - K4), Buzzer (not used).
* 1x Pico IO Shield KEYESTUDIO.
* 1x ESP32-WROOM-32 (basic experiments, OpenMQTTGateway).
* 1x DHT22 - Temperature & Humidity sensor.
* 1x LCD display - I2C 20 columns x 4 rows.
* 1x LCD display - 1.14 inch 240x135 resolution (Waveshare Pico-LCD-1.14).
* 1x LCD display - 3.5 inch 480x320 resolution (Waveshare Pico-ResTouch-LCD-3.5).
* 1x TM1637 - 4-digit 7-segment LED display (I2C).
* 1x Servo Motor - Tower Pro Micro Servo 9g SG90.
* 1x RFID-RC522 - Reader for MIFARE RFID Cards and Tokens.
* 1x TM1638 LED&KEY - 8x 7-segment decimal LED component with 8x individual LEDs and 8x push buttons.
* 1x PIR Motion Sensor.
* 1x Potentiometer.
* 2x DS18B20 - 1-wire digital thermometer.
* 1x 28BYJ-48 Stepper Motor with ULN2003 motor driver.
* 1x HC-SR04 Ultrasonic Distance Sensor.
* 1x IKEA VINDRIKTNING Air Quality sensor.
* 1x OVNSHVN ESP32 2.8" TFT Touch Screen Display ESP-32 WIFI BLE Dual Core.

## Credits
**THANKS**, to the developers of the Raspberry Pi & ESP Microcontroller, Domoticz Home Automation System, MicroPython Language, Libraries & Tools and to all sharing related information. Without these, it would not be possible to write this document.

## Licence
GNU GENERAL PUBLIC LICENSE v3.0.

The information shared for personal use only - use at your own risk (see LICENSE).

