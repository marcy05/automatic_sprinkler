import json
import network
from time import sleep
import machine
import time
import ntptime
from umqttsimple import MQTTClient

ssid = ""
password = ""
mqtt_server = ""
client_id = ""
user_t = ""
password_t = ""

current_time = time.localtime()
wlan = network.WLAN(network.STA_IF)

def connect():
    #Connect to WLAN
    print("Connecting...")
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)

def sync_time():
    global current_time
    if wlan.isconnected():
        ROME_OFFSET = 1*60*60
        ntptime.settime()
        
        current_time = time.localtime(time.time()+ROME_OFFSET)
        print("New time: {}".format(current_time))


def mqtt_connect():
    print("Connecting to MQTT server...")
    client = MQTTClient(client_id, mqtt_server, user=user_t, password=password_t, keepalive=60)
    client.connect()
    print('Connected to %s MQTT Broker'%(mqtt_server))
    return client

try:
    connect()
    print("Current time: {}".format(time.localtime()))
    sync_time()
    print("Current time: {}".format(time.time()+60*60))

    client = mqtt_connect()
    for i in range(10):
        topic = "hello"
        message = {"Test": True}
        client.publish(topic, msg="{}".format(str(message)))
    
except KeyboardInterrupt:
    machine.reset()