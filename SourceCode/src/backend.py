# #############################################################################
#                               IMPORT
# #############################################################################
import time
import network
from umqtt.simple import MQTTClient

import src.lib.my_ntp as my_ntp
from src.my_secret import secret
from src.simple_logger import SimpleLogger

# #############################################################################
#                          GLOBAL VARIABLES
# #############################################################################
logger = SimpleLogger()

# #############################################################################
#                               CLASSES
# #############################################################################
class BackEndInterface:
    def __init__(self) -> None:
        logger.debug("Init Backend interface")
        self.network_status = False
        self.network_ssid = ""
        self.network_password = ""
        self.ntp_sync_done = False
        self.mqtt_server_ip = ""
        self.client_id = ""
        self.mqtt_user = ""
        self.mqtt_password = ""
        self.mqtt_client = MQTTClient
        self.mqtt_status = False
        self.subscribed_tipic = "garden"

        self.wlan = network.WLAN(network.STA_IF)

        init_result = self._init_secret()

        if init_result:
            logger.debug("Backend interface correctly init.")
        else:
            logger.error("Not possible to init the Backend interface.")
        logger.debug("Init Backend finished.")

    def _init_secret(self) -> bool:
        try:
            self.network_ssid = secret["network_ssid"]
            self.network_password = secret["network_password"]
            self.mqtt_server_ip = secret["mqtt_server_ip"]
            self.client_id = secret["client_id"]
            self.mqtt_user = secret["mqtt_user"]
            self.mqtt_password = secret["mqtt_password"]
            return True
        except Exception:
            logger.error("Not possible to find secret file.")
            return False

    def init(self):
        self.connect()
        self.set_correct_time()
        self.mqtt_connect()  # TODO uncomment for MQTT iteraction

    def connect(self):
        logger.debug("Connecting...")
        self.wlan.active(True)
        self.wlan.connect(self.network_ssid, self.network_password)
        max_retries = 20
        for i in range(max_retries):
            if not self.wlan.isconnected():
                logger.debug("Connection retry {}/{}".format(i + 1, max_retries))
                time.sleep(1)
            else:
                logger.debug("Connected.")
                self.network_status = True
                break
        if not self.wlan.isconnected():
            logger.error("Not possible to connect to internet.")

    def sub_cb(self, topic, msg):
        logger.debug("New message on topic {}".format(topic.decode('utf-8')))
        msg = msg.decode('utf-8')
        logger.debug(msg)

    def mqtt_connect(self):
        logger.debug("Connecting to MQTT broker...")
        try:
            self.mqtt_client = MQTTClient(self.client_id,
                                          self.mqtt_server_ip,
                                          user=self.mqtt_user,
                                          password=self.mqtt_password,
                                          keepalive=60)
            logger.debug("MQTT Client set up")
            # logger.debug("Server: {}\nUser: {}\nPassword: {}".format(self.mqtt_server_ip,
            #                                                          self.mqtt_user,
            #                                                          self.mqtt_password))
            self.mqtt_client.set_callback(self.sub_cb)
            logger.debug("Callback set")
            for i in range(3):
                logger.debug("MQTT Connection retry: {}/3".format(i + 1))
                status = "N/A"
                time.sleep(1)
                try:
                    status = self.mqtt_client.connect()
                    break
                except Exception:
                    logger.warning("Connection refused: {}".format(status))
                    self.mqtt_status = False
                    return False
            logger.debug("Connected")
            self.mqtt_status = True
            logger.debug("Updated mqtt status")
            self.mqtt_client.subscribe(self.subscribed_tipic)
            logger.debug("Tipic subscribed")
            logger.debug("Connected to MQTT.")
        except Exception:
            logger.warning("Not possible to connect to MQTT!")

    def publish_to_topic(self, topic: str, msg: str):
        if self.mqtt_status:
            logger.debug("Publishing message...")
            self.mqtt_client.publish(topic, msg)
            logger.debug("Done")

    def set_correct_time(self):
        if self.network_status:
            if self.wlan.isconnected():
                try:
                    TIME_SHIFT = 2
                    my_ntp.settime(TIME_SHIFT)
                    self.ntp_sync_done = True
                    logger.debug("NTP time set: {}".format(time.localtime()))
                except Exception:
                    logger.warning("Not possible to set global time")
