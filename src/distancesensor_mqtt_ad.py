"""
File:   distancesensor_mqtt_ad.py
Date:   20230511
Author: Robert W.B. Linn
:description
Test MQTT auto discovery with Domoticz and the Pico W running as web server.
Domoticz Hardware: MQTT Auto Discovery Client Gateway with LAN Interface, Name=MQTTADGateway
Domoticz Devices created via MQTT auto discovery by publishing config topic (see domoticz log below).
The device is from type General, Distance.
:external libraries
umqtt.simple (https://github.com/micropython/micropython-lib/tree/master/micropython/umqtt.simple)
hcsr04 (https://github.com/rsc1975/micropython-hcsr04)
MQTT Remove Retained messages:
Distance Device:
mosquitto_sub -h localhost --remove-retained -t 'domoticz/sensor/distance/config' -W 1
ALL Devices:
mosquitto_sub -h localhost --remove-retained -t '#' -W 1
:domoticz log
NOTE:
Initially the Domoticz distance device is not in place.
The device is created first time by the MQTT topic "domoticz/sensor/distance/config" with payload {"name": "Distance", "device_class": "distance", "state_topic": "domoticz/sensor/distance/state", "value_template": "{{value_json.distance}}", "unit_of_measurement": "cm", "unique_id": "DIST001"}.
The state, i.e. updating the device value is set by the topic "domoticz/sensor/distance/state" with payload {"distance":NN.NN}
See below log for payload examples for the topic.
2023-05-10 15:37:05.978 Status: MQTTADGateway: discovered: DIST001/Distance (unique_id: DIST001)
2023-05-10 15:37:05.978 Debug: MQTTADGateway: topic: domoticz/sensor/distance/config, message: {"name": "Distance", "device_class": "distance", "state_topic": "domoticz/sensor/distance/state", "value_template": "{{value_json.distance}}", "unit_of_measurement": "cm", "unique_id": "DIST001"}
2023-05-10 15:37:06.083 MQTTADGateway: General/Distance (Distance)
2023-05-10 15:37:06.079 Debug: MQTTADGateway: topic: domoticz/sensor/distance/state, message: {"distance":12.78}
:thonny log
distance_mqtt_ad v20230512
Sampling Rate: 10s.
Network connecting...
Network connected: picow-ip
MQTT Broker connecting...
MQTT Broker connected: domoticz-ip
MQTT Autodiscover published: topic=domoticz/sensor/distance/config, payload={"name": "Distance", "device_class": "distance", "state_topic": "domoticz/sensor/distance/state", "value_template": "{{value_json.distance}}", "unit_of_measurement": "cm", "unique_id": "DIST001"}
MQTT published: topic=domoticz/sensor/distance/state, payload={"distance":12.78}
:wiring
(LLC = Logic Level Converter (3.3V-5V))
LLC = Pico W
LV1 = N/A
LV2 = N/A
LV	= 3V3 (OUT)
GND	= GND (Pin #38)
LV3 = GP14 (Pin #19)
LV4 = GP15 (Pin #20)
HV1 = N/A
HV2 = N/A
HV	= VBUS (Pin #40)
GND	= GND (Pin #38)
HV3	= N/A
HV4	= N/A
LLC = HC-SR04
LV1 = N/A
LV2 = N/A
LV	= N/A
GND	= N/A
LV3 = N/A
LV4 = N/A
HV1 = N/A
HV2 = N/A
HV	= VCC
GND	= GND
HV3	= Echo
HV4	= Trig
"""
# Imports
import network
import time
from machine import Pin
from utime import sleep, sleep_ms
# Installed via Thonny manage packages
from umqtt.simple import MQTTClient
# HCSR04 from hcsr04.py (must be uploaded to the pico)
from hcsr04 import HCSR04
# Call server from server.py (must be uploaded to the picow)
from server import Server
# Configuration (must be uploaded to the pico w)
import config
import sys
# Constants
VERSION = const('distance_mqtt_ad v20230512')
"""
DISTANCESENSOR HC-SR04
"""
# Sensor Pins
PIN_ECHO = 14
PIN_TRIG = 15
distance_sensor = HCSR04(trigger_pin=15, echo_pin=14)
"""
SAMPLING
"""
# Distance measurement sampling rate in seconds
SAMPLING_RATE = 10
"""
MQTT
"""
MQTT_BROKER		= config.DOMOTICZ_MQTT_IP
MQTT_CLIENT_ID	= const('picow_distance_sensor')
# Topic & payload to create the device. The configuration component is sensor.
DISTANCE_TOPIC_CONFIG	= const(b'domoticz/sensor/distance/config')
DISTANCE_PAYLOAD_CONFIG	= const(b'{"name": "Distance", "device_class": "distance", "state_topic": "domoticz/sensor/distance/state", "value_template": "{{value_json.distance}}", "unit_of_measurement": "cm", "unique_id": "DIST001"}')
# Topic used to publish the state of the sensor
# Payload is JSON format: {"distance":NN}
STATE_TOPIC		= const(b'domoticz/sensor/distance/state')
STATE_PAYLOAD   = '{"distance":{D}}'
def mqtt_connect(client_id, mqtt_server):
    """Connect to the MQTT broker with client id and server address"""
    client = MQTTClient(client_id, mqtt_server, keepalive=3600)
    client.connect()
    print(f'MQTT Broker connecting...')
    return client
def mqtt_reconnect():
    """Reconnect to the MQTT broker"""
    print('[ERROR] Failed to connect to the MQTT Broker. Reconnecting...')
    time.sleep(5)
    machine.reset()
def mqtt_init():
    """Connect to MQTT & Publish mqtt auto discovery topic & payload for the domoticz device"""
    try:
        # Connect to MQTT broker
        client = mqtt_connect(MQTT_CLIENT_ID, MQTT_BROKER)
        print(f'MQTT Broker connected: {MQTT_BROKER}')
        # Publish config topic to auto create the distance device in domoticz
        client.publish(DISTANCE_TOPIC_CONFIG, DISTANCE_PAYLOAD_CONFIG)
        print(f'MQTT Autodiscover published: topic={DISTANCE_TOPIC_CONFIG.decode()}, payload={DISTANCE_PAYLOAD_CONFIG.decode()}')
        return client
    
    except OSError as e:
        mqtt_reconnect()
# Info
print(f'{VERSION}')
print(f'Sampling Rate: {SAMPLING_RATE}s.')
# Create network object using the ssid & password from config.py
network = Server(config.WIFI_SSID, config.WIFI_PASSWORD, DEBUG=True)
# Connect to the network and get the server object
server = network.connect()
# Connect to MQTT
mqtt_client = mqtt_init()
    
# Main
while True:
    try:
        # Measure the distance and set the payload message (encoded as required by mqtt client publish)
        payload = STATE_PAYLOAD.replace('{D}', str(distance_sensor.distance_cm())).encode()
        # MQTT publish with encoded topic & payload (buffered objects required)
        mqtt_client.publish(STATE_TOPIC, payload)
        print(f'MQTT published: topic={STATE_TOPIC.decode()}, payload={payload.decode()}')
    except OSError as e:
        print(f'[ERROR] Can not get the distance {e}')
        
    # Delay till next sample
    sleep(SAMPLING_RATE)
