#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import os
import time

# Default configuration
config = {
    'mqtt': {
        'broker': os.getenv('MQTT_HOST', 'localhost'),
        'port': int(os.getenv('MQTT_PORT', '1883')),
        'prefix': os.getenv('MQTT_PREFIX', 'media'),
        'topic': os.getenv('MQTT_TOPIC', 'button'),
        'user': os.environ.get('MQTT_USER'),
        'password': os.environ.get('MQTT_PASSWORD'),
    },
    'button': {
        'channel': int(os.getenv('BUTTON_CHANNEL', '17')),
        'bouncetime': int(os.getenv('BUTTON_BOUNCETIME', '1000')),
    }
}

def mqtt_on_connect(client, userdata, flags, rc):
    """@type client: paho.mqtt.client """

    print("Connection returned result: "+str(rc))

def mqtt_send(value, retain=False):
    print("publishing " + config['mqtt']['prefix'] + "/" + config['mqtt']['topic'] + "=" + value)
    mqtt_client.publish(config['mqtt']['prefix'] + "/" + config['mqtt']['topic'], value, retain=retain)

def cleanup():
    print("cleanup")
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    GPIO.cleanup(config['button']['channel'])

def button_callback(channel):
    mqtt_send('push')

try:

    ### Setup MQTT ###
    print("Initialising MQTT...")
    mqtt_client = mqtt.Client(config['mqtt']['prefix'] + "-button-mqtt")
    if config['mqtt']['user']:
        mqtt_client.username_pw_set(config['mqtt']['user'], password=config['mqtt']['password']);
    mqtt_client.on_connect = mqtt_on_connect
    mqtt_client.connect(config['mqtt']['broker'], config['mqtt']['port'], 60)

    ### Setup GPIO ###
    print("Initializing GPIO...")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(config['button']['channel'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print("Initializing event...")
    GPIO.add_event_detect(config['button']['channel'], GPIO.FALLING, callback=button_callback, bouncetime=config['button']['bouncetime'])

    print("Starting main loop...")
    mqtt_client.loop_forever()
finally:
    cleanup()
