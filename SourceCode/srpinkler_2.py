import utime
import network
from my_secret import secret
from umqttsimple import MQTTClient

# #############################################################################
#                               CLASSES
# #############################################################################


class SimpleLogger:
    def debug(self, message: str):
        current_time = utime.gmtime(utime.time())
        formatted_date = "{}/{}/{} - {}:{}:{}".format(current_time[0],
                                                      current_time[1],
                                                      current_time[2],
                                                      current_time[3],
                                                      current_time[4],
                                                      current_time[5])
        print("{} - DEBUG - {}".format(formatted_date,
                                       message))

    def info(self, message: str):
        current_time = utime.gmtime(utime.time())
        formatted_date = "{}/{}/{} - {}:{}:{}".format(current_time[0],
                                                      current_time[1],
                                                      current_time[2],
                                                      current_time[3],
                                                      current_time[4],
                                                      current_time[5])
        print("{} - INFO - {}".format(formatted_date,
                                      message))

    def warning(self, message: str):
        current_time = utime.gmtime(utime.time())
        formatted_date = "{}/{}/{} - {}:{}:{}".format(current_time[0],
                                                      current_time[1],
                                                      current_time[2],
                                                      current_time[3],
                                                      current_time[4],
                                                      current_time[5])
        print("{} - WARNING - {}".format(formatted_date,
                                         message))

    def error(self, message: str):
        current_time = utime.gmtime(utime.time())
        formatted_date = "{}/{}/{} - {}:{}:{}".format(current_time[0],
                                                      current_time[1],
                                                      current_time[2],
                                                      current_time[3],
                                                      current_time[4],
                                                      current_time[5])
        print("{} - ERROR - {}".format(formatted_date,
                                       message))


class BackEndInterface:
    def __init__(self) -> None:
        logger.debug("Init Backend interface")
        self.network_ssid = ""
        self.network_password = ""
        self.mqtt_server_ip = ""
        self.client_id = ""
        self.user_raspberry = ""
        self.pass_rasberry = ""
        self.mqtt_client = MQTTClient

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
            self.user_raspberry = secret["user_raspberry"]
            self.pass_rasberry = secret["pass_rasberry"]
            return True
        except:
            logger.error("Not possible to find secret file.")
            return False

    def connect(self):
        logger.debug("Connecting...")
        self.wlan.active(True)
        self.wlan.connect(self.network_ssid, self.network_password)
        max_retries = 20
        for i in range(max_retries):
            if not self.wlan.isconnected():
                logger.debug("Connection retry {}/{}".format(i+1, max_retries))
                utime.sleep(1)
            else:
                logger.debug("Connected.")
                break
        if not self.wlan.isconnected():
            logger.error("Not possible to connect to internet.")

    def sub_cb(topic, msg):
        logger.debug("New message on topic {}".format(topic.decode('utf-8')))
        msg = msg.decode('utf-8')
        logger.debug(msg)

    def mqtt_connect(self):
        logger.debug("Connecting to MQTT broker...")
        self.mqtt_client = MQTTClient(self.client_id,
                                      self.mqtt_server_ip,
                                      user=self.user_raspberry,
                                      password=self.pass_rasberry,
                                      keepalive=60)
        self.mqtt_client.set_callback(self.sub_cb)
        self.mqtt_client.connect()

        logger.debug("Connected to MQTT.")



class Garden:
    def __init__(self) -> None:
        logger.debug("Init Gerden...")
        self.start_time = utime.time()
        self.last_execution_time = utime.time()
        self.last_logging_time = utime.time()

        self.exec_update_interval = 30  # Time in seconds
        self.log_update_interval = 20  # Time in seconds

        logger.debug("Init completed.")

        self.backend = BackEndInterface()

    def init_backend(self):
        self.backend.connect()
        self.backend.mqtt_connect()

    def _is_running_update_time_expired(self):
        if (utime.time() - self.last_execution_time) >= \
                self.exec_update_interval:
            self.last_execution_time = utime.time()
            return True
        return False

    def _is_logging_update_time_expired(self):
        if (utime.time() - self.last_logging_time) >= \
                self.log_update_interval:
            self.last_logging_time = utime.time()
            return True
        return False

    def run(self):
        if self._is_logging_update_time_expired():
            logger.debug("Running garden")


# #############################################################################
#                               GLOBAL VARIABLES
# #############################################################################
logger = SimpleLogger()
my_garden = Garden()
my_garden.init_backend()



# #############################################################################
#                               MAIN LOOP
# #############################################################################

while True:
    my_garden.run()
