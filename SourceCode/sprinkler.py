import utime
import network
import machine
import time
from my_secret import secret
from umqtt.simple import MQTTClient
import my_ntp

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
        self.network_status = False
        self.network_ssid = ""
        self.network_password = ""
        self.ntp_sync_done = False
        self.mqtt_server_ip = ""
        self.client_id = ""
        self.user_raspberry = ""
        self.pass_rasberry = ""
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
            self.user_raspberry = secret["user_raspberry"]
            self.pass_rasberry = secret["pass_rasberry"]
            return True
        except:
            logger.error("Not possible to find secret file.")
            return False

    def init(self):
        self.connect()
        self.set_correct_time()
        # self.mqtt_connect()  # TODO uncomment for MQTT iteraction

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
                                          user=self.user_raspberry,
                                          password=self.pass_rasberry,
                                          keepalive=60)
            self.mqtt_client.set_callback(self.sub_cb)
            self.mqtt_client.connect()
            self.mqtt_status = True
            self.mqtt_client.subscribe(self.subscribed_tipic)
            logger.debug("Connected to MQTT.")
        except:
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
                except:
                    logger.warning("Not possible to set global time")


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

    def _read_u16(self, adc_read: int) -> float:
        """
        Convert the Vdigit to Volt value from ADC.
        """
        return adc_read * 3.3 / 65535

    def get_analog_from_mux(self, channel: int) -> float:
        logger.debug("HwInterface - Channel: {} reading...".format(channel))
        self.a_s0.value(self.multiplex_selector[channel][0])
        self.a_s1.value(self.multiplex_selector[channel][1])
        self.a_s2.value(self.multiplex_selector[channel][2])
        self.a_s3.value(self.multiplex_selector[channel][3])
        volt = self._read_u16(self.a_sig.read_u16())
        return volt


class Pump:
    def __init__(self, pump_id: int) -> None:
        self.pump_id = pump_id
        self.status = True
        self.activation_period = 2  # Value in seconds

    def set_pump_value(self, signal: bool):
        logger.debug("Pump: {}, setting value: {}".format(self.pump_id,
                                                          signal))
        hw_interface = HwInterface()
        hw_interface.set_channel_value(self.pump_id, signal)

    def watering(self):
        self.set_pump_value(True)
        utime.sleep(self.activation_period)
        self.set_pump_value(False)


class Sensor:
    def __init__(self, sensor_id: int) -> None:
        self.sensor_id = sensor_id
        self.status = True
        self.active_threshold = 0.1
        self.current_value = 0.0

        self._check_activation()

    def _check_activation(self):
        hw_interface = HwInterface()
        sensor_value = hw_interface.get_analog_from_mux(self.sensor_id)
        self.status = True if sensor_value >= self.active_threshold else False

    def get_voltage(self):
        if self.status:
            hw_interface = HwInterface()
            self.current_value = hw_interface.get_analog_from_mux(self.sensor_id)
            return self.current_value
        else:
            return 0


class Garden:
    def __init__(self) -> None:
        logger.debug("Init Gerden...")
        self.start_time = utime.time()
        self.last_execution_time = utime.time()
        self.last_logging_time = utime.time()

        self.watering_timer = utime.time()
        self.watering_period = 1 * 24 * 60 * 60  # Days
        self.watering_period = 50  # TODO erase this for real application
        self.watering_iterations = 3
        self.watering_itersations_delay = 10  # seconds of delays between one watering action and another.

        self.back_sync_timer = utime.time()
        self.back_sync_period = 60 * 60  # Period of time for backend sync

        self.sensor_reading_timer = utime.time()
        self.sensor_reading_period = 20 * 60  # Sensor reading period
        self.sensor_reading_period = 10  # TODO erase this for real application

        #self.exec_update_interval = 5  # Time in seconds
        #self.log_update_interval = 50  # Time in seconds

        self.pumps = [Pump(i) for i in range(7)]
        self.sensors = [Sensor(i) for i in range(7)]

        logger.debug("Init completed.")

        self.backend = BackEndInterface()

    def init_timers(self):
        # This functions allows to sync all timers after that the NTP sync 
        #   has properly set the RTC time.
        init_time = utime.time()
        self.start_time = init_time
        self.last_execution_time = init_time
        self.last_logging_time = init_time
        self.watering_timer = init_time
        self.back_sync_timer = init_time
        self.sensor_reading_timer = init_time

    def _is_evening(self):
        tm = utime.gmtime(utime.time())
        month = tm[1]
        hour = tm[3]
        # Consider evening erlier in colder months
        if (month >= 1 and month <= 5) or (month >= 10 and month <= 12):
            if hour >= 18:
                return True
        # Consider evening late in hotter months
        if month > 5 and month < 10:
            if hour >= 19:
                return True

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

    def is_watering_moment(self):
        if (utime.time() - self.watering_timer) >= self.watering_period:
            logger.debug("Watering timeout expired")
            if self.backend.ntp_sync_done:
                logger.debug("NTP was sync")
                if self._is_evening():
                    logger.debug("Evening detected")
                    return True
                else:
                    return False
            else:
                logger.debug("NTP not sync. Watering timeout expired.")
                return True
        return False

    def pump_cycle(self):
        for iteration in range(self.watering_iterations):
            logger.debug("Watering iteration: {}/{}".format(iteration+1, self.watering_iterations))
            for pump in self.pumps:
                if pump.status:
                    pump.watering()
            utime.sleep(self.watering_itersations_delay)

    def is_backend_sync_moment(self):
        if (utime.time() - self.back_sync_timer) >= self.back_sync_period:
            logger.debug("Backend sync time")
            return True
        return False

    def send_data_to_back(self):
        # collect pums status
        # collect sensor status
        # collect sensor data
        # send data via mqtt
        pass

    def is_sensor_reading_moment(self):
        if (utime.time() - self.sensor_reading_timer) >= self.sensor_reading_period:
            logger.debug("Sensor reading moment")
            return True
        return False

    def reading_sensors(self):
        for i in range(len(self.sensors)):
            sensor_value = self.sensors[i].get_voltage()
            logger.debug("Sensor: {} -> Voltage: {}".format(i, sensor_value))

    def run(self):

        if self.is_watering_moment():
            self.pump_cycle()
            self.watering_timer = utime.time()

        if self.is_backend_sync_moment():
            self.send_data_to_back()
            self.back_sync_timer = utime.time()

        if self.is_sensor_reading_moment():
            self.reading_sensors()
            self.sensor_reading_timer = utime.time()


# #############################################################################
#                               GLOBAL VARIABLES
# #############################################################################
logger = SimpleLogger()

HwInterface().reset_digital_mux()

my_garden = Garden()
my_garden.backend.init()
my_garden.init_timers()


# #############################################################################
#                               MAIN LOOP
# #############################################################################

logger.debug("Entering main loop ->")
while True:
    my_garden.run()
