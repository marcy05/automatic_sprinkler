import paho.mqtt.client as mqtt
import paho.mqtt.subscribe as subscribe

def on_message(client, userdata, message):
    print("message: {}".format(message))
    print("Message received: ", str(message.payload.decode("utf-8")))
    print("Message topic: ", message.topic)

def on_connect(client, userdata, flags, rc):
    status={"0":"successful", "1":"refused-Incorrect protocol version", "2":"refused-Invalid client identifier", "3":"refused-server unavailable", "4":"refused-Bad User or Password", "5":"refused-Not authorised"}
    print("Connection status: ", status[str(rc)])

def main():
    print("Init client")
    client = mqtt.Client("SeverPI")
    client.username_pw_set(username="myUser", password="myPassword")
    print("Client subscribed")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("192.168.8.152", 1883, 60)
    print("Start looping...")
    client.subscribe("garden/#")
    client.loop_forever()


if __name__ == "__main__":
    main()
