# #############################################################################
#                               IMPORT
# #############################################################################
import os
import utime
import machine

from src.simple_logger import logger
from src.persistencyHandler import get_persisted_timers
from src.persistencyHandler import write_persistency_value

# #############################################################################
#                               CLASSES
# #############################################################################

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
        logger.debug(f"{self.__class__.__name__} - Start resetting all relays...")
        for channel in range(self.mux_channels_used):
            self.d_s0.value(self.multiplex_selector[channel][0])
            self.d_s1.value(self.multiplex_selector[channel][1])
            self.d_s2.value(self.multiplex_selector[channel][2])
            self.d_s3.value(self.multiplex_selector[channel][3])
            self.d_sig.value(False)
        logger.info(f"{self.__class__.__name__} - Reset relays done.")

    def set_channel_value(self, channel: int, signal: bool):
        logger.debug(f"{self.__class__.__name__} - Channel: {channel} with Value: {signal}")
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
        logger.debug(f"{self.__class__.__name__} - Channel: {channel} reading...")
        self.a_s0.value(self.multiplex_selector[channel][0])
        self.a_s1.value(self.multiplex_selector[channel][1])
        self.a_s2.value(self.multiplex_selector[channel][2])
        self.a_s3.value(self.multiplex_selector[channel][3])
        volt = self._read_u16(self.a_sig.read_u16())
        return volt

class Pump:
    def __init__(self, pump_id: int) -> None:
        self.pump_id = pump_id
        self.status = False
        self._activation_period = get_persisted_timers(f"P{self.pump_id}_activation_period")   # Value in seconds

    def set_activation_period(self, activation_perdiod: float) -> bool:
        try:
            write_persistency_value(f"P{self.pump_id}_activation_period", activation_perdiod)
            self._activation_period = activation_perdiod
            logger.info(f"{self.__class__.__name__} - Pump:{self.pump_id} - Activation period updated to:{self._activation_period}")
            return True
        except Exception as e:
            logger.warning(f"It was not possible to set the new activation value for Pump:{self.pump_id}")
            return False

    def get_activation_period(self) -> float:
        return self._activation_period

    def get_db_data(self) -> dict:
        data = {"Pump{}Status".format(self.pump_id): self.status,
                "Pump{}ActPeriod".format(self.pump_id): self.get_activation_period()}
        return data

    def get_str_data(self) -> str:
        data = f"P_{self.pump_id}_Status: {self.status}, P_{self.pump_id}_ActPeriod: {self._activation_period}"
        return data

    def get_db_status(self) -> dict:
        data = {"Pump{}Status".format(self.pump_id): self.status}
        return data

    def get_db_Act_period(self) -> dict:
        data = {"Pump{}ActPeriod".format(self.pump_id): self.get_activation_period()}
        return data

    def set_status(self, status: bool):
        self.status = status
        self.set_pump_value(status)

    def set_pump_value(self, signal: bool):
        logger.debug(f"{self.__class__.__name__}: {self.pump_id}, setting value: {signal}")
        hw_interface = HwInterface()
        hw_interface.set_channel_value(self.pump_id, signal)

    def watering(self):
        logger.info(f"{self.__class__.__name__} - Watering period started")
        self.set_pump_value(True)
        self.status = True
        utime.sleep(self.get_activation_period())
        self.set_pump_value(False)
        self.status = False
        logger.info(f"{self.__class__.__name__} - Watering period finished")


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

    def get_db_data(self) -> dict:
        logger.info(f"{self.__class__.__name__} - get sensors data")
        data = {f"Sensor{self.sensor_id}Status": self.status,
                f"Sensor{self.sensor_id}ActThreshold": self.active_threshold,
                f"Sensor{self.sensor_id}CurrentValue": self.current_value}
        return data

    def get_str_data(self) -> str:
        data = f"S_{self.sensor_id}_Status: {self.status}\nS_{self.sensor_id}_ActTRH: {self.active_threshold}\nS_{self.sensor_id}_Value: {self.current_value}"
        return data

    def get_db_status(self) -> dict:
        data = {f"Sensor{self.sensor_id}Status": self.status}
        return data

    def get_db_actThreshold(self) -> dict:
        data = {f"Sensor{self.sensor_id}ActThreshold": self.active_threshold}
        return data

    def get_db_current_val(self) -> dict:
        data = {f"Sensor{self.sensor_id}CurrentValue": self.current_value}
        return data

    def set_status(self, status: bool) -> None:
        self.status = status

    def set_threshold(self, threshold: float) -> None:
        self.active_threshold = threshold
