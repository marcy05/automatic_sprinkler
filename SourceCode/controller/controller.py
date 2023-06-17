import machine
import utime
import network
from umqtt.simple import MQTTClient
from secret import secret


class MqttClient:
    def __init__(self):
        self._wlan = network.WLAN(network.STA_IF)
        self.mqtt_client = MQTTClient

        self.subscribed_tipic = "garden"

        self.connect()
        self.mqtt_connect()

        self.connection_error_count = 0

    def connect(self):
        print("Connecting...")
        self._wlan.active(True)
        self._wlan.connect(secret["network_ssid"], secret["network_password"])
        max_retries = 20
        for i in range(max_retries):
            if not self._wlan.isconnected():
                print("Connection retry {}/{}".format(i+1, max_retries))
                utime.sleep(1)
            else:
                print("Connected.")
                self.network_status = True
                break
        if not self._wlan.isconnected():
            print("Not possible to connect to internet.")
    
    def disconnect(self):
        try:
            print("Try to disconnect")
            self.mqtt_client.disconnect()
        except Exception as err:
            print(f"Not possible to disconnect. Reason: {err}")

    def sub_cb(self, topic, msg):
        print("New message on topic {}".format(topic.decode('utf-8')))
        msg = msg.decode('utf-8')
        print(msg)

    def mqtt_connect(self):
        print("Connecting to MQTT broker...")
        try:
            self.mqtt_client = MQTTClient(secret["client_id"],
                                          secret["mqtt_server_ip"],
                                          user=secret["mqtt_user"],
                                          password=secret["mqtt_password"],
                                          keepalive=60)
            print("MQTT Client set up")

            self.mqtt_client.set_callback(self.sub_cb)
            print("Callback set")
            for i in range(2):
                print("MQTT Connection retry: {}/2".format(i+1))
                status = "N/A"
                utime.sleep(.5)
                try:
                    status = self.mqtt_client.connect()
                    break
                except Exception:
                    print("Connection refused: {}".format(status))
                    if i == 2:
                        return False
            print("MQTT Connected")
            print("Subscribe...")
            try:
                self.mqtt_client.subscribe(self.subscribed_tipic)
                print("Tipic subscribed")
            except Exception:
                print("ERROR - MQTT No subscription possible")
                return False
            print("MQTT Connection completed.")
        except Exception:
            print("Not possible to connect to MQTT!")


class Button:
    def __init__(self, button_id: int = 99, button_gpio: int = 99, led_gpio: int = 99):
        self.button_id: int = button_id
        self._button_gpio: int = button_gpio
        self._led_gpio: int = led_gpio

        self.button = machine.Pin(
            self._button_gpio, machine.Pin.IN, machine.Pin.PULL_UP)
        self.led = machine.Pin(self._led_gpio, machine.Pin.OUT)

    def trigger_led(self):
        self.led.value(1)
        utime.sleep(.2)
        self.led.value(0)


class Controller:
    def __init__(self) -> None:
        self._controller_gpio = {
            0: {"button": 2,
                "led": 3},
            1: {"button": 4,
                "led": 5},
            2: {"button": 6,
                "led": 7},
            3: {"button": 8,
                "led": 9},
            4: {"button": 10,
                "led": 11},
            5: {"button": 12,
                "led": 13},
            6: {"button": 14,
                "led": 15},
        }

        self.button_list = [Button(key, self._controller_gpio[key]["button"],
                                   self._controller_gpio[key]["led"]) for key in self._controller_gpio]
        
    def welcome_animation(self):
        for button in self.button_list:
            button.led.value(1)
            utime.sleep(.2)
            button.led.value(0)


# #### GLOBAL VARIABLE
controller = Controller()
backend = MqttClient()
# ####  GLOBAL FUNCTIONS


def set_up():
    global controller

    controller.welcome_animation()


def main():
    while True:
        for button_item in controller.button_list:
            if not button_item.button.value():
                button_item.trigger_led()
                try:
                    topic = "garder/pump{}".format(button_item.button_id)
                    msg = "activate"
                    backend.mqtt_client.publish(topic, msg)
                    print(f'Sent - Topic: {topic} - Message: {msg}')
                    utime.sleep(1)
                except Exception as err:
                    print(f"Was not possible to send message to the backend because: {err}")

                    backend.connection_error_count += 1

                    if backend.connection_error_count >= 2:
                        backend.disconnect()
                        backend.mqtt_connect()
          
# ####  MAIN


set_up()
main()
