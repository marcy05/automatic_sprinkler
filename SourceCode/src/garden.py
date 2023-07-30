# #############################################################################
#                               IMPORT
# #############################################################################
import json
import utime
import _thread

from src.simple_logger import SimpleLogger, LogLevels
from src.hw_interface import HwInterface, Sensor, Pump
from src.backend import BackEndInterface
# #############################################################################
#                          GLOBAL VARIABLES
# #############################################################################
logger = SimpleLogger(LogLevels.INFO)

# #############################################################################
#                               CLASSES
# #############################################################################
class Garden:
    def __init__(self) -> None:
        logger.info(f"{self.__class__.__name__} - Init Gerden...")
        self.start_time = utime.time()

        self.watering_timer = utime.time()
        self.daily_watering_done = False
        self.watering_period = 1 * 24 * 60 * 60  # Days
        self.watering_period = 50  # TODO erase this for real application
        self.watering_iterations = 3
        self.watering_itersations_delay = 10  # seconds of delays between one watering action and another.

        self.back_sync_timer = utime.time()
        self.back_sync_period = 60 * 60  # Period of time for backend sync
        self.back_sync_period = 10  # TODO erase for real application

        self.sensor_reading_timer = utime.time()
        self.sensor_reading_period = 20 * 60  # Sensor reading period
        self.sensor_reading_period = 10  # TODO erase this for real application
        logger.debug(f"{self.__class__.__name__} - [ok] timers and period initialized")

        self.pumps = [Pump(i) for i in range(7)]
        self.sensors = [Sensor(i) for i in range(7)]

        logger.debug(f"{self.__class__.__name__} - [ok] pumps and sensors initialized")

        self.backend = BackEndInterface()
        logger.debug(f"{self.__class__.__name__} - [ok] backend initialized")

        self.backend_sync_thread = _thread.start_new_thread(self.thread_backend_sync, ())

        logger.info(f"{self.__class__.__name__} - [ok] Init completed.")

    def init_timers(self):
        # This functions allows to sync all timers after that the NTP sync
        #   has properly set the RTC time.
        init_time = utime.time()
        self.start_time = init_time
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

    def is_watering_moment(self):
        if not self.daily_watering_done:
            if (utime.time() - self.watering_timer) >= self.watering_period:
                if self.backend.ntp_sync_done:
                    if self._is_evening():
                        self.daily_watering_done = True
                        return True
                    else:
                        return False
                else:
                    logger.debug(f"{self.__class__.__name__} - NTP not sync. Watering timeout expired.")
                    self.daily_watering_done = True
                    return True
            return False
        return False

    def pump_cycle(self):
        for iteration in range(self.watering_iterations):
            logger.debug(f"{self.__class__.__name__} - Watering iteration: {iteration + 1}/{self.watering_iterations}")
            for pump in self.pumps:
                pump.watering()
            utime.sleep(self.watering_itersations_delay)

    def is_backend_sync_moment(self):
        if (utime.time() - self.back_sync_timer) >= self.back_sync_period:
            logger.debug(f"{self.__class__.__name__} - Backend sync time")
            return True
        return False

    def _collect_data(self) -> dict:
        data_dict = {}

        for pump in self.pumps:
            data_dict[f"Plant{pump.pump_id}"] = pump.get_db_data()

        for sensor in self.sensors:
            plant = data_dict[f"Plant{sensor.sensor_id}"]
            sensor_data = sensor.get_db_data()
            for entry in sensor_data:
                plant[entry] = sensor_data[entry]
            data_dict[f"Plant{sensor.sensor_id}"] = plant

        just_value = {}
        for plant in data_dict:
            data = data_dict[plant]
            for key in data:
                just_value[key] = data[key]

        return just_value

    def _dict_2_str(self, conv_data: dict) -> str:
        return json.dumps(conv_data)

    def send_data_to_back(self):
        logger.debug(f"{self.__class__.__name__} - Collecting data...")
        if self.backend.mqtt_status:
            str_data = self._dict_2_str(self._collect_data())
            logger.info(f"{self.__class__.__name__} - [ok] data collected")
        else:
            logger.debug(f"{self.__class__.__name__} - No mqtt registered, data collection skipped.")

        if self.backend.mqtt_status:
            self.backend.mqtt_client.publish("garden/status", str_data)
            logger.debug(f"{self.__class__.__name__} - MQTT - Pump status sent")

    def is_sensor_reading_moment(self):
        if (utime.time() - self.sensor_reading_timer) >= self.sensor_reading_period:
            logger.debug(f"{self.__class__.__name__} - Sensor reading moment")
            return True
        return False

    def reading_sensors(self):
        for i in range(len(self.sensors)):
            sensor_value = self.sensors[i].get_voltage()
            logger.debug(f"{self.__class__.__name__} - Sensor: {i} -> Voltage: {sensor_value}")

    def thread_backend_sync(self):
        while True:
            try:
                if self.is_backend_sync_moment():
                    self.send_data_to_back()
                    self.back_sync_timer = utime.time()
            except AttributeError as e:
                logger.error(f"{self.__class__.__name__} - Thread error! Exception: {e}")
                utime.sleep(2)
            except Exception:
                utime.sleep(2)
                pass

    def run(self):

        if self.is_watering_moment():
            self.pump_cycle()
            self.watering_timer = utime.time()

        if self.is_sensor_reading_moment():
            self.reading_sensors()
            self.sensor_reading_timer = utime.time()
