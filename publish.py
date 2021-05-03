#!/usr/bin/python
import paho.mqtt.client as mqtt
import time
import os
import sys
import datetime
import RPi.GPIO as GPIO

thingid = os.getenv('thingid','distance')
brokeraddr = os.getenv('brokeraddr','openhabian')
refresh = int(os.getenv('refresh', '5'))
pin_trigger = int(os.getenv('pintrigger', '18'))
pin_echo = int(os.getenv('pinecho', '24'))

thingTopic = "jumajumo/" + thingid + "/"

client = mqtt.Client(thingid)

client.will_set(thingTopic + "sys/state", "OFFLINE", qos=1, retain=True)

client.connect(brokeraddr, keepalive=3600)

client.loop_start()

client.publish(thingTopic, str(datetime.datetime.now()), qos=1, retain=True)
client.publish(thingTopic + "sys/type", "sensor", qos=1, retain=True)
client.publish(thingTopic + "sys/device", "distance", qos=1, retain=True)

client.publish(thingTopic + "env/thingid", thingid, qos=1, retain=True)
client.publish(thingTopic + "env/brokeraddr", brokeraddr, qos=1, retain=True)
client.publish(thingTopic + "env/refresh", refresh, qos=1, retain=True)
client.publish(thingTopic + "env/pintrigger", pin_trigger, qos=1, retain=True)
client.publish(thingTopic + "env/pinecho", pin_echo, qos=1, retain=True)

GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_trigger, GPIO.OUT)
GPIO.setup(pin_echo, GPIO.IN)

def measure():
    GPIO.output(pin_trigger, True)
    time.sleep(0.00001)
    GPIO.output(pin_trigger, False)

    startTime = time.time()
    stopTime = time.time()

    while GPIO.input(pin_echo) == 0:
        startTime = time.time()

    while GPIO.input(pin_echo) == 1:
        stopTime = time.time()

    timeElapsed = stopTime - startTime

    # mit der Schallgeschwindigkeit (34300 cm/s) multiplizieren
    # und durch 2 teilen, da hin und zurueck
    distance = (timeElapsed * 34300) / 2

    return distance


try:
    while True:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin_trigger, GPIO.OUT)
        GPIO.setup(pin_echo, GPIO.IN)

        value1 = measure()
        time.sleep(0.2)
        value2 = measure()
        time.sleep(0.2)
        value3 = measure()
        time.sleep(0.2)
        value4 = measure()
        time.sleep(0.2)
        value5 = measure()
        time.sleep(0.2)
        value6 = measure()
        time.sleep(0.2)
        value7 = measure()
        time.sleep(0.2)
        value8 = measure()
        time.sleep(0.2)
        value9 = measure()
        time.sleep(0.2)
        value10 = measure()

        calculated = (value1+value2+value3+value4+value5+value6+value7+value8+value9+value10) / 10

        client.publish(thingTopic + "sys/state", "ONLINE", qos=2, retain=True)
        client.publish(thingTopic + "distance", calculated, qos=1, retain=False)

        time.sleep(refresh)

except:
    GPIO.cleanup()
    client.disconnect()
    client.loop_stop()
