# #############################################################################
#                               IMPORT
# #############################################################################
import json
import utime

import src.const as const

from src.simple_logger import logger
from src.hw_interface import Sensor, Pump, WaterLevel
from src.backend import BackEndInterface
from src.backend import TelegramMessage
from src.persistencyHandler import get_int_from_json, get_float_from_json
from src.persistencyHandler import write_persistency_value
from src.utils_func import str2bool, status2bool

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
        self._tank_level = WaterLevel()
        self._pump_deactivation_sem = False

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

    def is_tank_full(self) -> bool:
        if self._tank_level.is_tank_full():
            return True
        else:
            return False

    def _deactivate_all_pumps(self) -> None:
        logger.info(f"{self.__class__.__name__} - Deactivating all pumps...")
        for pump in self.pumps:
            pump.set_status(False)
        logger.info(f"{self.__class__.__name__} - All pumps deactivated")

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
                if pump.get_active_status():
                    pump.watering()
                else:
                    logger.debug(f"The pump:{pump.pump_id} has Active status to False. It will be skipped")
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
                         f"Sensor reading period = {self.sensor_reading_period}\n"

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

    def _set_pump_active_status(self, pump_id: int, active_status: bool) -> None:
        for pump in self.pumps:
            if pump.pump_id == pump_id:
                pump.set_active_status(active_status)
                break

    def __reply_sensor_data(self, msg: TelegramMessage):
        logger.info("Retrieving sensors data")
        self.backend.bot.send(msg.chat_id, f"Sensors:\n{self._get_sensors_data()}")

    def __reply_pumps_data(self, msg: TelegramMessage):
        logger.info("Retrieving pumps data")
        self.backend.bot.send(msg.chat_id, f"Pumps:\n{self._get_pumps_data()}")

    def __reply_garden_timers(self, msg: TelegramMessage):
        logger.info("Retrieving garden timers")
        self.backend.bot.send(msg.chat_id, self._get_garden_timers())

    def __reply_pump_status(self, msg: TelegramMessage):
        split_msg = msg.msg_text.split("_")
        pump_id = int(split_msg[const.ENTITY_FIELD].replace("p", ""))
        status_str = split_msg[const.VALUE_FIELD].lower()
        status = str2bool(status_str)
        logger.info(f"Pump status: {status}")
        self._set_pump_status(pump_id, status)
        self.backend.bot.send(msg.chat_id, "Command successfully executed")

    def __reply_activation_period(self, msg: TelegramMessage):
        split_msg = msg.msg_text.split("_")
        pump_id = int(split_msg[const.ENTITY_FIELD].replace("p", ""))
        activation_period = float(split_msg[const.VALUE_FIELD])
        logger.info(f"Activation for Pump: {pump_id} will change to: {activation_period}")
        result = self._set_pump_activation_period(pump_id, activation_period)
        if result:
            self.backend.bot.send(msg.chat_id, "Command successfully executed")
        else:
            self.backend.bot.send(msg.chat_id, "Command executed unsuccessfully")

    def __reply_sensor_status(self, msg: TelegramMessage):
        split_msg = msg.msg_text.split("_")
        sensor_id = int(split_msg[const.ENTITY_FIELD].replace("s", ""))
        status_str = split_msg[const.VALUE_FIELD]
        status = str2bool(status_str)
        logger.info(f"Sensor status: {status}")
        self._set_sensor_status(sensor_id, status)
        self.backend.bot.send(msg.chat_id, "Command successfully executed")

    def __reply_watering_iterations(self, msg: TelegramMessage):
        logger.debug("Setting Watering iterations...")
        split_msg = msg.msg_text.split("_")
        watering_iterations = int(split_msg[const.VALUE_FIELD])
        write_persistency_value("garden_watering_iteration", watering_iterations)
        self.watering_iterations = get_int_from_json("garden_watering_iteration", self._timers_persistency_path)

        logger.info(f"Watering iteration correctly set to: {self.watering_iterations}")
        self.backend.bot.send(msg.chat_id, f"Watering iteration correctly set to: {self.watering_iterations}")

    def __reply_watering_iterations_delay(self, msg: TelegramMessage):
        logger.debug("Setting watering delay...")
        split_msg = msg.msg_text.split("_")
        watering_delay = float(split_msg[const.VALUE_FIELD])
        write_persistency_value("garden_water_iteration_delay", watering_delay)
        self.watering_itersations_delay = get_float_from_json("garden_water_iteration_delay", self._timers_persistency_path)

        logger.info(f"Watering iteration delay correctly set to: {self.watering_itersations_delay}")
        self.backend.bot.send(msg.chat_id, f"Watering iteration delay correctly set to: {self.watering_itersations_delay}")

    def __reply_sensor_reading_period(self, msg: TelegramMessage):
        logger.debug("Setting sensor reading period...")
        split_msg = msg.msg_text.split("_")
        reading_period = float(split_msg[const.VALUE_FIELD])
        write_persistency_value("sensor_reading_period", reading_period)
        self.sensor_reading_period = get_float_from_json("sensor_reading_period", self._timers_persistency_path)

        logger.info(f"Reading period correctly set to: {self.sensor_reading_period}")
        self.backend.bot.send(msg.chat_id, f"Reading period correctly set to: {self.sensor_reading_period}")

    def __reply_backend_sync_period(self, msg: TelegramMessage):
        logger.debug("Setting backend sync period...")
        split_msg = msg.msg_text.split("_")
        sync_period = float(split_msg[const.VALUE_FIELD])
        write_persistency_value("backend_sync_period", sync_period)
        self.back_sync_period = get_float_from_json("backend_sync_period", self._timers_persistency_path)

        logger.info(f"Backend sync period set correctly to: {self.back_sync_period}")
        self.backend.bot.send(msg.chat_id, f"Backend sync period set correctly to: {self.back_sync_period}")

    def __is_valid_set_message(self, msg: TelegramMessage):
        splitted_msg = msg.msg_text.split("_")
        if len(splitted_msg) == 4:
            try:
                entity = splitted_msg[const.ENTITY_FIELD]
                command = splitted_msg[const.ENTITY_COMMAND]
                value = splitted_msg[const.VALUE_FIELD]
                return True
            except Exception as e:
                logger.warning(f"Unexpected exception: {e}")
                self.backend.bot.send("The command was not successful, check your paramenters")
                return False
        else:
            logger.warning("Set message with not correct number of arguments")
            self.backend.bot.send(msg.chat_id, "Set message with not correct number of arguments")
            return False

    def __forced_watering_cycle(self, msg: TelegramMessage):
        logger.info("Start forced watering cycle")
        self.backend.bot.send(msg.chat_id, "Start forced watering cycle")
        self.pump_cycle()
        logger.info("Watering cycle completed")
        self.backend.bot.send(msg.chat_id, "Finished forced watering cycle")

    def __reply_active_pump(self, msg: TelegramMessage):
        logger.debug("Setting new active status for pump...")
        split_msg = msg.msg_text.split("_")
        pump_id = int(split_msg[const.ENTITY_FIELD].replace("p", ""))
        status_str = split_msg[const.VALUE_FIELD].lower()
        active_status = status2bool(status_str)
        self._set_pump_active_status(pump_id, active_status)
        logger.info(f"Pump: {pump_id} set Active status: {active_status} successfully")
        self.backend.bot.send(msg.chat_id, f"Pump: {pump_id} set Active status: {active_status} successfully")

    def evaluate_data_from_telegram(self):
        logger.info(f"{self.__class__.__name__} - Listening to Telegram")
        t_msg = self.backend.bot.read_once()
        try:
            if t_msg is not None:
                logger.info(f"{self.__class__.__name__} - ID: {t_msg.sender_id} message: {t_msg.msg_text}")

                if t_msg.msg_text == "/get_sensors_data":
                    self.__reply_sensor_data(t_msg)

                elif t_msg.msg_text == "/get_pumps_data":
                    self.__reply_pumps_data(t_msg)

                elif t_msg.msg_text == "/get_garden_timers":
                    self.__reply_garden_timers(t_msg)

                elif t_msg.msg_text == "/force_watering_cycle":
                    self.__forced_watering_cycle(t_msg)

                elif "/set_" in t_msg.msg_text:
                    logger.info("Set event detected")
                    if self.__is_valid_set_message(t_msg):

                        split_msg = t_msg.msg_text.split("_")

                        entity = split_msg[const.ENTITY_FIELD]  # pump, sensor, garden, backend
                        command = split_msg[const.ENTITY_COMMAND]
                        value = split_msg[const.VALUE_FIELD]

                        if "p" in entity and len(entity) == 2:
                            logger.info("Pump set event detected")
                            pump_id = int(entity.replace("p", ""))
                            logger.info(f"Pump id: {pump_id}")

                            if "stat" in command.lower():
                                self.__reply_pump_status(t_msg)

                            elif "actperiod" in command.lower():
                                self.__reply_activation_period(t_msg)

                            elif "active" in command.lower():
                                self.__reply_active_pump(t_msg)

                            else:
                                logger.warning("Command not found in Pump")
                                self.backend.bot.send(t_msg.chat_id, "Command not found in Pump")

                        elif "s" in entity and len(entity) == 2:
                            logger.info("Sensor set event detected")
                            sensor_id = int(entity.replace("s", ""))
                            logger.info(f"Sensor id: {sensor_id}")

                            if "stat" in command:
                                self.__reply_sensor_status(t_msg)
                            else:
                                logger.warning("Command not found for Sensor")
                                self.backend.bot.send(t_msg.chat_id, "Command not found for Sensor")

                        elif "garden" in split_msg[const.ENTITY_FIELD]:
                            logger.info("Garden set event detected")

                            if "wateringIterations" in command:
                                self.__reply_watering_iterations(t_msg)

                            elif "waterIterDelay" in command:
                                self.__reply_watering_iterations_delay(t_msg)

                            elif "sensorReadingPeriod" in command:
                                self.__reply_sensor_reading_period(t_msg)
                            else:
                                logger.warning("Command not found in Garden")
                                self.backend.bot.send(t_msg.chat_id, "Command not found in Garden")

                        elif "backend" in split_msg[const.ENTITY_FIELD]:
                            logger.info("Backend set event detected")

                            if "syncPeriod" in command:
                                self.__reply_backend_sync_period(t_msg)

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
        if self.is_tank_full():
            self._pump_deactivation_sem = True
            if self.is_watering_moment():
                self.pump_cycle()
                self.watering_timer = utime.time()
        else:
            if self._pump_deactivation_sem:
                self._pump_deactivation_sem = False
                self._deactivate_all_pumps()

        if self.is_sensor_reading_moment():
            self.reading_sensors()
            self.sensor_reading_timer = utime.time()

        if self.is_log_moment():
            logger.info(f"{self.__class__.__name__} - System alive")
            self.log_bit_timer = utime.time()
            self.evaluate_data_from_telegram()
