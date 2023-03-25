import time
import paho.mqtt.client as mqtt


# This is the Subscriber

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("Time")

def on_message(client, userdata, msg):
    print(msg.payload)

client = mqtt.Client(client_id="Controller1")
client.username_pw_set("pico", "picopassword")
client.connect("192.168.8.152",1883,60)

client.on_connect = on_connect
client.on_message = on_message

for i in range(10):
        client.publish('Time', payload="payload_test", qos=0, retain=False)
        print("Message sent from Controller")
        time.sleep(2)


# client.loop_forever()