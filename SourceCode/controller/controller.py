import machine
import utime
import network
from umqtt.simple import MQTTClient
from secret import secret

class MqttClient:
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.mqtt_client = MQTTClient
        self.network_ssid = secret["network_ssid"]
        self.network_password = secret["network_password"]
        self.mqtt_server_ip = secret["mqtt_server_ip"]
        self.client_id = secret["client_id"]
        self.mqtt_user = secret["mqtt_user"]
        self.mqtt_password = secret["mqtt_password"]
        self.subscribed_tipic = "garden"

        self.connect()
        self.mqtt_connect()
    
    def connect(self):
        print("Connecting...")
        self.wlan.active(True)
        self.wlan.connect(self.network_ssid, self.network_password)
        max_retries = 20
        for i in range(max_retries):
            if not self.wlan.isconnected():
                print("Connection retry {}/{}".format(i+1, max_retries))
                utime.sleep(1)
            else:
                print("Connected.")
                self.network_status = True
                break
        if not self.wlan.isconnected():
            print("Not possible to connect to internet.")
    
    def sub_cb(self, topic, msg):
        print("New message on topic {}".format(topic.decode('utf-8')))
        msg = msg.decode('utf-8')
        print(msg)
    
    def mqtt_connect(self):
        print("Connecting to MQTT broker...")
        try:
            self.mqtt_client = MQTTClient(self.client_id,
                                          self.mqtt_server_ip,
                                          user=self.mqtt_user,
                                          password=self.mqtt_password,
                                          keepalive=60)
            print("MQTT Client set up")
            # print("Server: {}\nUser: {}\nPassword: {}".format(self.mqtt_server_ip,
            #                                                          self.mqtt_user,
            #                                                          self.mqtt_password))
            self.mqtt_client.set_callback(self.sub_cb)
            print("Callback set")
            for i in range(3):
                print("MQTT Connection retry: {}/3".format(i+1))
                status = "N/A"
                utime.sleep(.5)
                try:
                    status = self.mqtt_client.connect()
                    break
                except:
                    print("Connection refused: {}".format(status))
                    if i == 2:
                        return False
            print("MQTT Connected")
            print("Subscribe...")
            try:
                self.mqtt_client.subscribe(self.subscribed_tipic)
                print("Tipic subscribed")
            except:
                print("ERROR - MQTT No subscription possible")
                return False
            print("MQTT Connection completed.")
        except:
            print("Not possible to connect to MQTT!")

class Button:
    def __init__(self, Button_id:int = 99, button_gpio:int = 99, red_gpio:int = 99, green_gpio:int = 99):
        self.Button_id: int = Button_id
        self._button_gpio: int = button_gpio
        self._red_gpio: int = red_gpio
        self._green_gpio: int = green_gpio

        self.button = machine.Pin(self._button_gpio, machine.Pin.IN, machine.Pin.PULL_UP)
        self.red = machine.Pin(self._red_gpio, machine.Pin.OUT)
        self.green = machine.Pin(self._green_gpio, machine.Pin.OUT)


# #### GLOBAL VARIABLE
p0 = Button(0, 5, 28, 27)
p1 = Button(1, 6, 26, 22)
p2 = Button(2, 7, 21, 20)
p3 = Button(3, 8, 19, 18)
p4 = Button(4, 9, 17, 16)
p5 = Button(5, 10, 12, 13)
p6 = Button(6, 11, 14, 15)
Button_list = [p0, p1, p2, p3, p4, p5, p6]

# ####  GLOBAL FUNCTIONS

def set_on_red():
    for Button in Button_list:
        Button.red.value(1)
    print("Set all red on")

def set_off_red():
    for Button in Button_list:
        Button.red.value(0)
    print("Set all red off")

def set_on_green():
    for Button in Button_list:
        Button.green.value(1)
    print("Set all green on")

def set_off_green():
    for Button in Button_list:
        Button.green.value(0)
    print("Set all green off")

def start_animation():
    print("Start animation")
    for Button in Button_list:
        Button.red.value(1)
        utime.sleep(.1)
        Button.red.value(0)
        Button.green.value(1)
        utime.sleep(.1)
        Button.green.value(0)
    print("Finish animation")

# ####  MAIN

backend = MqttClient()
set_off_green()
set_off_red()
start_animation()

print("Entering infinite loop")
while False:

    if not p0.button.value():
        p0.green.value(1)
        p0.red.value(1)
        utime.sleep(.5)
        p0.green.value(0)
        p0.red.value(0)
        utime.sleep(.5)
    if not p1.button.value():
        p1.green.value(1)
        p1.red.value(1)
        utime.sleep(.5)
        p1.green.value(0)
        p1.red.value(0)
        utime.sleep(.5)
    if not p2.button.value():
        p2.green.value(1)
        p2.red.value(1)
        utime.sleep(.5)
        p2.green.value(0)
        p2.red.value(0)
        utime.sleep(.5)
    if not p3.button.value():
        p3.green.value(1)
        p3.red.value(1)
        utime.sleep(.5)
        p3.green.value(0)
        p3.red.value(0)
        utime.sleep(.5)
    if not p4.button.value():
        p4.green.value(1)
        p4.red.value(1)
        utime.sleep(.5)
        p4.green.value(0)
        p4.red.value(0)
        utime.sleep(.5)
    if not p5.button.value():
        p5.green.value(1)
        p5.red.value(1)
        utime.sleep(.5)
        p5.green.value(0)
        p5.red.value(0)
        utime.sleep(.5)
    if not p6.button.value():
        p6.green.value(1)
        p6.red.value(1)
        utime.sleep(.5)
        p6.green.value(0)
        p6.red.value(0)
        utime.sleep(.5)
    utime.sleep(.2)