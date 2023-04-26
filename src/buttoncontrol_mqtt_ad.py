"""
File:   buttoncontrol_mqtt_ad.py
Date:   20230425
Author: Robert W.B. Linn
:description
Test MQTT auto discovery with Domoticz and the Pico W running as web server.
Domoticz Hardware: MQTT Auto Discovery Client Gateway with LAN Interface, Name=MQTTADGateway
Domoticz Device created via MQTT auto discovery by publishing config topic (see domoticz log below).
The autodiscover component is button and the Domoticz device is type=Light/Switch. 
Note that this script does not use the library server.py but has simple code to connect to the network.
:external libraries
umqtt.simple
MQTT Remove Retained message for creating the button:
mosquitto_sub -h localhost --remove-retained -t 'domoticz/button/makelab/config' -W 1
Restart Domoticz:
sudo service domoticz.sh restart
 
:thonny log
buttoncontrol_mqtt_ad v20230425
Network connecting...
Network connected: webserver-ip
MQTT Broker connecting...
MQTT Broker connected: NNN.NNN.NNN.179
MQTT State published: topic=domoticz/button/makelab/config, payload={"name": "MakeLabButton", "state_topic": "domoticz/button/makelab/state", "unique_id": "BM001"}
MQTT published: topic=domoticz/button/makelab/state, payload={"ON"}
:wiring
Button = Pico W
Button K4 = GP20 (Pin #26)
GND (-) = GND (Pin #28)
"""
# Imports
import network
import time
from machine import Pin
# picozero - BETA version (Installed via Thonny manage packages)
from picozero import Button
# mqtt simple (Installed via Thonny manage packages)
from umqtt.simple import MQTTClient
# Configuration (must be uploaded to the pico w)
import config
# Constants
VERSION = const('buttoncontrol_mqtt_ad v20230425')
"""
BUTTON
"""
# Button K4 pin
BUTTON_PINNR = 20
# Button object
btn = Button(BUTTON_PINNR)
# MQTT publish with encoded topic & payload (buffered objects required).
# The topic is the state_topic as defined in the configuration.
# The payload is the string ON (uppercase).
def button_pressed():
    client.publish(STATE_TOPIC, STATE_PAYLOAD)
    print(f'MQTT published: topic={STATE_TOPIC.decode()}, payload={STATE_PAYLOAD.decode()}')
# Set the function to run if the button is pressed
btn.when_pressed = button_pressed
"""
MQTT
"""
MQTT_BROKER		= const('NNN.NNN.NNN.179')
MQTT_CLIENT_ID	= const('picow_button_k4')
# Topic & payload to create the device. The configuration component is button.
BUTTON_TOPIC_CONFIG	= const(b'domoticz/button/makelab/config')
BUTTON_PAYLOAD_CONFIG	= const(b'{"name": "MakeLabButton", "state_topic": "domoticz/button/makelab/state", "unique_id": "BM001"}')
# Topic used to publish the state of the button
# Payload is JSON format (uppercase): {"ON"}
STATE_TOPIC		= const(b'domoticz/button/makelab/state')
STATE_PAYLOAD   = const(b'{"ON"}')
# Connect to the MQTT broker with client id and server address
def mqtt_connect(client_id, mqtt_server):
    client = MQTTClient(client_id, mqtt_server, keepalive=3600)
    client.connect()
    print(f'MQTT Broker connecting...')
    return client
# Reconnect to the MQTT broker
def mqtt_reconnect():
    print('[ERROR] Failed to connect to the MQTT Broker. Reconnecting...')
    time.sleep(5)
    machine.reset()
    
# Info
print(f'{VERSION}')
# Connect to the network
try:
    print(f'Network connecting...')
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
    time.sleep(5)
    if not wlan.isconnected():
        raise RuntimeError('[ERROR] Can not connect to the network.')  
    print(f'Network connected: {wlan.ifconfig()[0]}')
except Exception as e:
    raise RuntimeError('[ERROR] Can not connect to the network.')  
    
# Connect to MQTT
# Publish mqtt auto discovery topic & payload for the switch device (button)
try:
    # Connect to MQTT broker
    client = mqtt_connect(MQTT_CLIENT_ID, MQTT_BROKER)
    print(f'MQTT Broker connected: {MQTT_BROKER}')
    # Publish config topics to auto create the device in domoticz
    client.publish(BUTTON_TOPIC_CONFIG, BUTTON_PAYLOAD_CONFIG)
    print(f'MQTT State published: topic={BUTTON_TOPIC_CONFIG.decode()}, payload={BUTTON_PAYLOAD_CONFIG.decode()}')
except OSError as e:
    mqtt_reconnect()
# Main
while True:
    pass
