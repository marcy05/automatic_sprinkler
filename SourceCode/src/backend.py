# #############################################################################
#                               IMPORT
# #############################################################################
import time
import network
from umqtt.simple import MQTTClient

import src.lib.my_ntp as my_ntp
from src.my_secret import secret
from src.simple_logger import SimpleLogger, LogLevels

# #############################################################################
#                          GLOBAL VARIABLES
# #############################################################################
logger = SimpleLogger(LogLevels.INFO)

# #############################################################################
#                               CLASSES
# #############################################################################
class BackEndInterface:
    def __init__(self) -> None:
        logger.info(f"{self.__class__.__name__} - Init Backend interface")
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
            logger.debug(f"{self.__class__.__name__} - Backend interface correctly init.")
        else:
            logger.error(f"{self.__class__.__name__} - Not possible to init the Backend interface.")
        logger.debug(f"{self.__class__.__name__} - Init Backend finished.")

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
            logger.error(f"{self.__class__.__name__} - Not possible to find secret file.")
            return False

    def init(self):
        self.connect()
        self.set_correct_time()
        self.mqtt_connect()  # TODO uncomment for MQTT iteraction

    def connect(self):
        logger.info(f"{self.__class__.__name__} - Connecting...")
        self.wlan.active(True)
        self.wlan.connect(self.network_ssid, self.network_password)
        max_retries = 20
        for i in range(max_retries):
            if not self.wlan.isconnected():
                logger.debug(f"{self.__class__.__name__} - Connection retry {i + 1}/{max_retries}")
                time.sleep(1)
            else:
                logger.debug(f"{self.__class__.__name__} - Connected.")
                self.network_status = True
                break
        if not self.wlan.isconnected():
            logger.error(f"{self.__class__.__name__} - Not possible to connect to internet.")

    def sub_cb(self, topic, msg):
        logger.debug(f"{self.__class__.__name__} - New message on topic {topic.decode('utf-8')}")
        msg = msg.decode('utf-8')
        logger.debug(msg)

    def mqtt_connect(self):
        logger.info(f"{self.__class__.__name__} - Connecting to MQTT broker...")
        try:
            self.mqtt_client = MQTTClient(self.client_id,
                                          self.mqtt_server_ip,
                                          user=self.mqtt_user,
                                          password=self.mqtt_password,
                                          keepalive=60)
            logger.debug(f"{self.__class__.__name__} - MQTT Client set up")
            # logger.debug("Server: {}\nUser: {}\nPassword: {}".format(self.mqtt_server_ip,
            #                                                          self.mqtt_user,
            #                                                          self.mqtt_password))
            self.mqtt_client.set_callback(self.sub_cb)
            logger.debug(f"{self.__class__.__name__} - Callback set")
            for i in range(3):
                logger.debug(f"{self.__class__.__name__} - MQTT Connection retry: {i + 1}/3")
                status = "N/A"
                time.sleep(1)
                try:
                    status = self.mqtt_client.connect()
                    break
                except Exception:
                    logger.warning(f"{self.__class__.__name__} - Connection refused: {status}")
                    self.mqtt_status = False
                    return False
            if self.mqtt_status:
                self.mqtt_status = True
                logger.debug(f"{self.__class__.__name__} - Updated mqtt status")
                self.mqtt_client.subscribe(self.subscribed_tipic)
                logger.debug(f"{self.__class__.__name__} - Tipic subscribed")
                logger.info(f"{self.__class__.__name__} - Connected to MQTT.")
        except Exception:
            logger.warning(f"{self.__class__.__name__} - Not possible to connect to MQTT!")

    def publish_to_topic(self, topic: str, msg: str):
        if self.mqtt_status:
            logger.debug(f"{self.__class__.__name__} - Publishing message...")
            self.mqtt_client.publish(topic, msg)
            logger.info(f"{self.__class__.__name__} - Pubished message.")

    def set_correct_time(self):
        if self.network_status:
            if self.wlan.isconnected():
                try:
                    TIME_SHIFT = 2
                    my_ntp.settime(TIME_SHIFT)
                    self.ntp_sync_done = True
                    logger.info(f"{self.__class__.__name__} - NTP time set: {time.localtime()}")
                except Exception:
                    logger.warning(f"{self.__class__.__name__} - Not possible to set global time")
