import utime
import network
import machine
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


class HwInterface:
    def __init__(self) -> None:
        self.mux_channels_used = 7

        self.__pump_sig = 10
        self.__pump_s3 = 11
        self.__pump_s2 = 12
        self.__pump_s1 = 13
        self.__pump_s0 = 15

        self.__sensor_sig = 26
        self.__sensor_s3 = 18
        self.__sensor_s2 = 19
        self.__sensor_s1 = 20
        self.__sensor_s0 = 21

        self.d_s0 = machine.Pin(self.__pump_s0, machine.Pin.OUT)
        self.d_s1 = machine.Pin(self.__pump_s1, machine.Pin.OUT)
        self.d_s2 = machine.Pin(self.__pump_s2, machine.Pin.OUT)
        self.d_s3 = machine.Pin(self.__pump_s3, machine.Pin.OUT)
        self.d_sig = machine.Pin(self.__pump_sig, machine.Pin.OUT)

        self.a_s0 = machine.Pin(self.__sensor_s0, machine.Pin.OUT)
        self.a_s1 = machine.Pin(self.__sensor_s1, machine.Pin.OUT)
        self.a_s2 = machine.Pin(self.__sensor_s2, machine.Pin.OUT)
        self.a_s3 = machine.Pin(self.__sensor_s3, machine.Pin.OUT)
        self.a_sig = machine.ADC(self.__sensor_sig)

        self.multiplex_selector = [(0, 0, 0, 0),
                                   (1, 0, 0, 0),
                                   (0, 1, 0, 0),
                                   (1, 1, 0, 0),
                                   (0, 0, 1, 0),
                                   (1, 0, 1, 0),
                                   (0, 1, 1, 0),
                                   (1, 1, 1, 0),
                                   (0, 0, 0, 1),
                                   (1, 0, 0, 1),
                                   (0, 1, 0, 1),
                                   (1, 1, 0, 1),
                                   (0, 0, 1, 1),
                                   (1, 0, 1, 1),
                                   (0, 1, 1, 1),
                                   (1, 1, 1, 1)]

    def reset_digital_mux(self):
        logger.debug("HwInterface - Resetting all relays...")
        for channel in range(self.mux_channels_used):
            self.d_s0.value(self.multiplex_selector[channel][0])
            self.d_s1.value(self.multiplex_selector[channel][1])
            self.d_s2.value(self.multiplex_selector[channel][2])
            self.d_s3.value(self.multiplex_selector[channel][3])
            self.d_sig.value(False)
        logger.debug("HwInterface - Reset done.")

    def set_channel_value(self, channel: int, signal: bool):
        logger.debug("HwInterface - Channel: {} with Value: {}".format(channel,
                                                                       signal))
        self.d_s0.value(self.multiplex_selector[channel][0])
        self.d_s1.value(self.multiplex_selector[channel][1])
        self.d_s2.value(self.multiplex_selector[channel][2])
        self.d_s3.value(self.multiplex_selector[channel][3])
        self.d_sig.value(signal)

class Pump:
    def __init__(self, pump_id: int) -> None:
        self.pump_id = pump_id
        self.status = False

    def set_pump_value(self, signal: bool):
        logger.debug("Pump: {}, setting value: {}".format(self.pump_id,
                                                          signal))
        hw_interface = HwInterface()
        hw_interface.set_channel_value(self.pump_id, signal)


class Garden:
    def __init__(self) -> None:
        logger.debug("Init Gerden...")
        self.start_time = utime.time()
        self.last_execution_time = utime.time()
        self.last_logging_time = utime.time()

        self.exec_update_interval = 30  # Time in seconds
        self.log_update_interval = 20  # Time in seconds

        self.pumps = [Pump(i) for i in range(7)]

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

        if self._is_running_update_time_expired():
            self.pumps[0].set_pump_value(True)

        if self._is_logging_update_time_expired():
            logger.debug("Running garden")


# #############################################################################
#                               GLOBAL VARIABLES
# #############################################################################
logger = SimpleLogger()
my_garden = Garden()
my_garden.init_backend()

HwInterface().reset_digital_mux()

# #############################################################################
#                               MAIN LOOP
# #############################################################################

while True:
    my_garden.run()
