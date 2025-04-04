#!/usr/bin/python
import paho.mqtt.client as mqtt
import time
import os
import datetime
import RPi.GPIO as GPIO
import statistics

# Umgebungsvariablen abrufen
thingid = os.getenv('thingid', 'distance')
brokeraddr = os.getenv('brokeraddr', 'openhabian')
refresh = int(os.getenv('refresh', '5'))
pin_trigger = int(os.getenv('pintrigger', '18'))
pin_echo = int(os.getenv('pinecho', '24'))

thingTopic = "jumajumo/" + thingid + "/"

# MQTT-Client initialisieren
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, thingid)

# Letzter Wille: Wenn der Client sich abrupt trennt, wird eine Nachricht gesendet, die den Status auf "OFFLINE" setzt
client.will_set(thingTopic + "sys/state", "OFFLINE", qos=1, retain=True)

# MQTT-Server verbinden
client.connect(brokeraddr, keepalive=3600)
client.loop_start()

# MQTT-Initialisierung
client.publish(thingTopic + "sys/state", "ONLINE", qos=2, retain=True)

# GPIO-Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_trigger, GPIO.OUT)
GPIO.setup(pin_echo, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Pull-Down für stabilen Signalpegel

def measure():
    """ Misst die Entfernung mit dem HC-SR04 Sensor """
    GPIO.output(pin_trigger, True)
    time.sleep(0.00001)  # 10 Mikrosekunden Triggerpulse
    GPIO.output(pin_trigger, False)

    # Fixen Timeout-Wert von 40ms setzen (für größere Distanzen ausreichend)
    timeout = 0.04  # Timeout auf 40ms setzen

    # Warte auf Echo-Signal (Startzeit)
    start_time = None
    while GPIO.input(pin_echo) == 0:
        if time.time() > timeout:
            return None  # Timeout überschritten, kein Echo erhalten

    start_time = time.time()

    # Warte bis Echo-Signal endet (Stopzeit)
    while GPIO.input(pin_echo) == 1:
        if time.time() > timeout:
            return None  # Timeout überschritten, Echo nicht empfangen

    stop_time = time.time()

    if start_time is None or stop_time is None:
        return None  # Fehlerhafte Messung

    # Berechne die Distanz
    time_elapsed = stop_time - start_time
    distance = (time_elapsed * 34300) / 2  # Schallgeschwindigkeit: 34300 cm/s

    # Timeout auf max. 400cm begrenzen, falls die Entfernung größer wird
    if distance > 400:
        return None  # Werte, die über 400 cm hinausgehen, ignorieren

    return distance

try:
    while True:
        values = [measure() for _ in range(10)]
        valid_values = [v for v in values if v is not None]  # Filtere ungültige Messwerte raus

        if valid_values:
            calculated = statistics.median(valid_values)  # Median-Filter für stabilere Werte
        else:
            calculated = -1  # Fehlerwert

        log_message = f"{datetime.datetime.now()} - Distanz: {calculated:.2f} cm"
        client.publish(thingTopic + "sys/logmsg", log_message, qos=2, retain=True)
        client.publish(thingTopic + "distance", calculated, qos=1, retain=False)

        time.sleep(refresh)

except Exception as e:
    error_message = f"{datetime.datetime.now()} - Fehler: {str(e)}"
    client.publish(thingTopic + "sys/logmsg", error_message, qos=2, retain=True)

finally:
    # Sicherstellen, dass immer der Offline-Status gesendet wird, wenn das Skript beendet wird
    try:
        if client.is_connected():
            # "Offline"-Nachricht senden, bevor das Skript endet
            client.publish(thingTopic + "sys/state", "OFFLINE", qos=1, retain=True)
            client.disconnect()
    except Exception as e:
        error_message = f"{datetime.datetime.now()} - Disconnect-Fehler: {str(e)}"
        client.publish(thingTopic + "sys/logmsg", error_message, qos=2, retain=True)

    # GPIO sauber aufräumen
    GPIO.cleanup()
    # MQTT-Schleife stoppen
    client.loop_stop()
