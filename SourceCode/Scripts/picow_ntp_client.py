import json
import network
from time import sleep
import machine
import time
import ntptime
from umqtt.simple import MQTTClient
from secret import secret
import utime

ssid = secret["ssid"]
password = secret["password"]
mqtt_server = secret["mqtt_server"]
client_id = secret["client_id"]
user_t = secret["user_t"]
password_t = secret["password_t"]

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

def add_offset(offset: int = 0):
    # Function introduced waiting for pull request https://github.com/micropython/micropython-lib/pull/635
    current_time = utime.time()
    changed_time = current_time + offset*60*60
    # Returns (year, month, mday, hour, minute, second, weekday, yearday)
    new_time = utime.gmtime(changed_time)
    print("Changing to: {}".format(new_time))

    # Accpets (year, month, day, weekday, hours, minutes, seconds, subseconds)
    machine.RTC().datetime((new_time[0], new_time[1], new_time[2], new_time[6] + 1, new_time[3], new_time[4], new_time[5], 0))


def sync_time():
    global current_time
    if wlan.isconnected():

        # ntptime.settime() # waiting for https://github.com/micropython/micropython-lib/pull/635
        h_shift = 1  # UTC+1
        add_offset(h_shift)
        
        print("New time: {}".format(time.localtime()))


def mqtt_connect():
    print("Connecting to MQTT server...")
    client = MQTTClient(client_id, mqtt_server, user=user_t, password=password_t, keepalive=60)
    client.set_callback(sub_cb)
    client.connect()
    print("Connected")
    return client

def sub_cb(topic, msg):
    print("New message on topic {}".format(topic.decode('utf-8')))
    msg = msg.decode('utf-8')
    print(msg)

try:
    connect()
    print("Current time: {}".format(time.localtime()))
    sync_time()
    print("Current time: {}".format(time.localtime()))

    client = mqtt_connect()
    for i in range(10):
        print("Sending MQTT message")
        topic = "hello"
        message = {"Test": True}
        client.publish(topic, msg="{}".format(str(message)))
        sleep(2)
    

    for i in range(1000):
        print("Listening... {}".format(i))
        client.subscribe("Time")
        sleep(1)
    
except KeyboardInterrupt:
    machine.reset()