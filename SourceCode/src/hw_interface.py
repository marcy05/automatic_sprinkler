# #############################################################################
#                               IMPORT
# #############################################################################
import machine
import utime

from src.simple_logger import SimpleLogger

# #############################################################################
#                          GLOBAL VARIABLES
# #############################################################################
logger = SimpleLogger()

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
        logger.debug("HwInterface - Resetting all relays...")
        for channel in range(self.mux_channels_used):
            self.d_s0.value(self.multiplex_selector[channel][0])
            self.d_s1.value(self.multiplex_selector[channel][1])
            self.d_s2.value(self.multiplex_selector[channel][2])
            self.d_s3.value(self.multiplex_selector[channel][3])
            self.d_sig.value(False)
        logger.debug("HwInterface - Reset done.")

    def set_channel_value(self, channel: int, signal: bool):
        logger.debug("HwInterface - Channel: {} with Value: {}".format(channel, signal))
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
        self.status = False
        self._activation_period = 2   # Value in seconds

    def set_activation_period(self, activation_perdiod: float) -> None:
        self._activation_period = activation_perdiod

    def get_activation_period(self) -> float:
        return self._activation_period

    def get_db_data(self) -> dict:
        data = {"Pump{}Status".format(self.pump_id): self.status,
                "Pump{}ActPeriod".format(self.pump_id): self.get_activation_period()}
        return data

    def get_db_status(self) -> dict:
        data = {"Pump{}Status".format(self.pump_id): self.status}
        return data

    def get_db_Act_period(self) -> dict:
        data = {"Pump{}ActPeriod".format(self.pump_id): self.get_activation_period()}
        return data

    def set_pump_value(self, signal: bool):
        logger.debug("Pump: {}, setting value: {}".format(self.pump_id,
                                                          signal))
        hw_interface = HwInterface()
        hw_interface.set_channel_value(self.pump_id, signal)

    def watering(self):
        self.set_pump_value(True)
        self.status = True
        utime.sleep(self.get_activation_period())
        self.set_pump_value(False)
        self.status = False


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
        data = {"Sensor{}Status".format(self.sensor_id): self.status,
                "Sensor{}ActThreshold".format(self.sensor_id): self.active_threshold,
                "Sensor{}CurrentValue".format(self.sensor_id): self.current_value}
        return data

    def get_db_status(self) -> dict:
        data = {"Sensor{}Status".format(self.sensor_id): self.status}
        return data

    def get_db_actThreshold(self) -> dict:
        data = {"Sensor{}ActThreshold".format(self.sensor_id): self.active_threshold}
        return data

    def get_db_current_val(self) -> dict:
        data = {"Sensor{}CurrentValue".format(self.sensor_id): self.current_value}
        return data
