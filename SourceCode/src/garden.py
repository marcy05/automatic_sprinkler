# #############################################################################
#                               IMPORT
# #############################################################################
import json
import utime

from src.simple_logger import logger
from src.hw_interface import Sensor, Pump
from src.backend import BackEndInterface
from src.persistencyHandler import get_int_from_json, get_float_from_json
from src.persistencyHandler import write_persistency_value

# #############################################################################
#                               CLASSES
# #############################################################################
class Garden:
    def __init__(self) -> None:
        logger.info(f"{self.__class__.__name__} - Init Gerden...")

        self._timers_persistency_path = "src/timers.json"

        self.start_time = utime.time()

        self.watering_timer = utime.time()
        self.daily_watering_done = False
        self.watering_period = 1 * 24 * 60 * 60  # Days in seconds
        self.watering_period = 50  # TODO erase this for real application
        self.watering_iterations = get_int_from_json("garden_watering_iteration", self._timers_persistency_path)
        self.watering_itersations_delay = get_int_from_json("garden_water_iteration_delay", self._timers_persistency_path)  # seconds of delays between one watering action and another.

        self.back_sync_timer = utime.time()
        self.back_sync_period = get_int_from_json("backend_sync_period", self._timers_persistency_path)  # Period of time for backend sync in seconds

        self.sensor_reading_timer = utime.time()
        self.sensor_reading_period = get_int_from_json("sensor_reading_period", self._timers_persistency_path)  # Sensor reading period in seconds

        self.log_bit_timer = utime.time()
        self.log_bit_period = 2  # Log heartbit in seconds
        logger.debug(f"{self.__class__.__name__} - [ok] timers and period initialized")

        self.pumps = [Pump(i) for i in range(7)]
        self.sensors = [Sensor(i) for i in range(7)]

        logger.debug(f"{self.__class__.__name__} - [ok] pumps and sensors initialized")

        self.backend = BackEndInterface()
        logger.debug(f"{self.__class__.__name__} - [ok] backend initialized")

        logger.info(f"{self.__class__.__name__} - [ok] Init completed.")

    def init_timers(self):
        # This functions allows to sync all timers after that the NTP sync
        #   has properly set the RTC time.
        init_time = utime.time()
        self.start_time = init_time
        self.watering_timer = init_time
        self.back_sync_timer = init_time
        self.sensor_reading_timer = init_time
        self.log_bit_timer = init_time

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

    def _get_sensors_data(self) -> str:
        sensors_data = ""
        for sensor in self.sensors:
            sensors_data += f"{sensor.get_str_data()}\n\n"
        return sensors_data

    def _get_pumps_data(self) -> str:
        pumps_data = ""
        for pump in self.pumps:
            pumps_data += f"{pump.get_str_data()}\n\n"
        return pumps_data

    def _get_garden_timers(self) -> str:
        gardent_timers = f"Watering iterations = {self.watering_iterations}\n" + \
                         f"Watering iteration delay = {self.watering_itersations_delay}\n" + \
                         f"Backend communication delay = {self.back_sync_period}\n" + \
                         f"Sensor reading persiod = {self.sensor_reading_period}\n"

        return gardent_timers

    def _set_pump_status(self, pump_id: int, status: bool) -> None:
        for pump in self.pumps:
            if pump.pump_id == pump_id:
                pump.set_status(status)
                break

    def _set_pump_activation_period(self, pump_id: int, pump_actTime: float) -> bool:
        for pump in self.pumps:
            if pump.pump_id == pump_id:
                result = pump.set_activation_period(pump_actTime)
                return result

    def _set_sensor_status(self, sensor_id: int, status: bool) -> None:
        for sensor in self.sensors:
            if sensor.sensor_id == sensor_id:
                sensor.set_status(status)
                break

    def evaluate_data_from_telegram(self):
        logger.info(f"{self.__class__.__name__} - Listening to Telegram")
        t_msg = self.backend.bot.read_once()
        try:
            if t_msg is not None:
                logger.info(f"{self.__class__.__name__} - ID: {t_msg.sender_id} message: {t_msg.msg_text}")

                ENTITY_FIELD = 1
                ENTITY_COMMAND = 2
                VALUE_FIELD = 3

                if t_msg.msg_text == "/get_sensors_data":
                    logger.info("Retriving sensors data")
                    self.backend.bot.send(t_msg.chat_id, f"Sensors:\n{self._get_sensors_data()}")
                elif t_msg.msg_text == "/get_pumps_data":
                    logger.info("Retriving pumps data")
                    self.backend.bot.send(t_msg.chat_id, f"Pumps:\n{self._get_pumps_data()}")
                elif t_msg.msg_text == "/get_garden_timers":
                    self.backend.bot.send(t_msg.chat_id, self._get_garden_timers())

                elif "/set_" in t_msg.msg_text:
                    logger.info("Set event detected")
                    split_msg = t_msg.msg_text.split("_")

                    if "p" in split_msg[ENTITY_FIELD] and len(split_msg[ENTITY_FIELD]) == 2:
                        logger.info("Pump set event detected")
                        pump_id = int(split_msg[ENTITY_FIELD].replace("p", ""))
                        logger.info(f"Pump id: {pump_id}")

                        if "stat" in split_msg[ENTITY_COMMAND]:
                            status_str = split_msg[VALUE_FIELD].lower()
                            if status_str == "false":
                                status = False
                            elif status_str == "true":
                                status = True
                            logger.info(f"Pump status: {status}")
                            self._set_pump_status(pump_id, status)
                            self.backend.bot.send(t_msg.chat_id, "Command successfully executed")

                        elif "actperiod" in split_msg[ENTITY_COMMAND].lower():
                            activation_period = float(split_msg[VALUE_FIELD])
                            logger.info(f"Activation for Pump: {pump_id} will change to: {activation_period}")
                            result = self._set_pump_activation_period(pump_id, activation_period)
                            if result:
                                self.backend.bot.send(t_msg.chat_id, "Command successfully executed")
                            else:
                                self.backend.bot.send(t_msg.chat_id, "Command executed unsuccessfully")

                        else:
                            logger.warning("Command not found in Pump")
                            self.backend.bot.send(t_msg.chat_id, "Command not found in Pump")

                    elif "s" in split_msg[ENTITY_FIELD] and len(split_msg[ENTITY_FIELD]) == 2:
                        logger.info("Sensor set event detected")
                        sensor_id = int(split_msg[ENTITY_FIELD].replace("s", ""))
                        logger.info(f"Sensor id: {sensor_id}")

                        if "stat" in split_msg[ENTITY_COMMAND]:
                            status_str = split_msg[VALUE_FIELD]
                            if status_str == "false":
                                status = False
                            elif status_str == "true":
                                status = True
                            logger.info(f"Sensor status: {status}")
                            self._set_sensor_status(sensor_id, status)
                            self.backend.bot.send(t_msg.chat_id, "Command successfully executed")
                        else:
                            logger.warning("Command not found for Sensor")
                            self.backend.bot.send(t_msg.chat_id, "Command not found for Sensor")

                    elif "garden" in split_msg[ENTITY_FIELD]:
                        logger.info("Garden set event detected")

                        if "wateringIterations" in split_msg[ENTITY_COMMAND]:
                            logger.debug("Setting Watering iterations...")
                            watering_iterations = int(split_msg[VALUE_FIELD])
                            write_persistency_value("garden_watering_iteration", watering_iterations)
                            self.watering_iterations = get_int_from_json("garden_watering_iteration", self._timers_persistency_path)

                            logger.info(f"Watering iteration correctly set to: {self.watering_iterations}")
                            self.backend.bot.send(t_msg.chat_id, f"Watering iteration correctly set to: {self.watering_iterations}")

                        elif "waterIterDelay" in split_msg[ENTITY_COMMAND]:
                            logger.debug("Setting watering delay...")
                            watering_delay = float(split_msg[VALUE_FIELD])
                            write_persistency_value("garden_water_iteration_delay", watering_delay)
                            self.watering_itersations_delay = get_float_from_json("garden_water_iteration_delay", self._timers_persistency_path)

                            logger.info(f"Watering iteration delay correctly set to: {self.watering_itersations_delay}")
                            self.backend.bot.send(t_msg.chat_id, f"Watering iteration delay correctly set to: {self.watering_itersations_delay}")

                        elif "sensorReadingPeriod" in split_msg[ENTITY_COMMAND]:
                            logger.debug("Setting sensor reading period...")
                            reading_period = float(split_msg[VALUE_FIELD])
                            write_persistency_value("sensor_reading_period", reading_period)
                            self.sensor_reading_period = get_float_from_json("sensor_reading_period", self._timers_persistency_path)

                            logger.info(f"Reading period correctly set to: {self.sensor_reading_period}")
                            self.backend.bot.send(t_msg.chat_id, f"Reading period correctly set to: {self.sensor_reading_period}")

                        else:
                            logger.warning("Command not found in Garden")
                            self.backend.bot.send(t_msg.chat_id, "Command not found in Garden")

                    elif "backend" in split_msg[ENTITY_FIELD]:
                        logger.info("Backend set event detected")

                        if "syncPeriod" in split_msg[ENTITY_COMMAND]:
                            logger.debug("Setting backend sync period...")
                            sync_period = float(split_msg[VALUE_FIELD])
                            write_persistency_value("backend_sync_period", sync_period)
                            self.back_sync_period = get_float_from_json("backend_sync_period", self._timers_persistency_path)

                            logger.info(f"Backend sync period set correctly to: {self.back_sync_period}")
                            self.backend.bot.send(t_msg.chat_id, f"Backend sync period set correctly to: {self.back_sync_period}")

                        else:
                            logger.warning("Command not found in backend")
                            self.backend.bot.send(t_msg.chat_id, "Command not found in backend")

                    else:
                        self.backend.bot.send(t_msg.chat_id, "Command not recognized")
            else:
                logger.debug(f"{self.__class__.__name__} - No new messages from Telegram.")
        except Exception as e:
            logger.error(f"Not possible to parse the message because: {e}")
            self.backend.bot.send(t_msg.chat_id, "Not possible to parse the message")

    def is_sensor_reading_moment(self):
        if (utime.time() - self.sensor_reading_timer) >= self.sensor_reading_period:
            logger.debug(f"{self.__class__.__name__} - Sensor reading moment")
            return True
        return False

    def reading_sensors(self):
        for i in range(len(self.sensors)):
            sensor_value = self.sensors[i].get_voltage()
            logger.debug(f"{self.__class__.__name__} - Sensor: {i} -> Voltage: {sensor_value}")

    def is_log_moment(self):
        if (utime.time() - self.log_bit_timer) >= self.log_bit_period:
            return True
        return False

    def run(self):

        if self.is_watering_moment():
            self.pump_cycle()
            self.watering_timer = utime.time()

        if self.is_sensor_reading_moment():
            self.reading_sensors()
            self.sensor_reading_timer = utime.time()

        if self.is_log_moment():
            logger.info(f"{self.__class__.__name__} - System alive")
            self.log_bit_timer = utime.time()
            self.evaluate_data_from_telegram()
