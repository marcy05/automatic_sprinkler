import time
import machine


class SimpleLogger:
    def debug(self, message: str):
        current_time = time.gmtime(time.time())
        formatted_date = "{}/{}/{} - {}:{}:{}".format(current_time[0],
                                                      current_time[1],
                                                      current_time[2],
                                                      current_time[3],
                                                      current_time[4],
                                                      current_time[5])
        print("{} - DEBUG - {}".format(formatted_date,
                                       message))

    def info(self, message: str):
        current_time = time.gmtime(time.time())
        formatted_date = "{}/{}/{} - {}:{}:{}".format(current_time[0],
                                                      current_time[1],
                                                      current_time[2],
                                                      current_time[3],
                                                      current_time[4],
                                                      current_time[5])
        print("{} - INFO - {}".format(formatted_date,
                                      message))

    def warning(self, message: str):
        current_time = time.gmtime(time.time())
        formatted_date = "{}/{}/{} - {}:{}:{}".format(current_time[0],
                                                      current_time[1],
                                                      current_time[2],
                                                      current_time[3],
                                                      current_time[4],
                                                      current_time[5])
        print("{} - WARNING - {}".format(formatted_date,
                                         message))

    def error(self, message: str):
        current_time = time.gmtime(time.time())
        formatted_date = "{}/{}/{} - {}:{}:{}".format(current_time[0],
                                                      current_time[1],
                                                      current_time[2],
                                                      current_time[3],
                                                      current_time[4],
                                                      current_time[5])
        print("{} - ERROR - {}".format(formatted_date,
                                       message))

logger = SimpleLogger()

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
        return True

    def watering(self):
        print("Pump:{} Start".format(self.pump_id))
        self.set_pump_value(True)
        time.sleep(self.activation_period)
        self.set_pump_value(False)


    
pumps = [Pump(i) for i in range(7)]

for pump in pumps:
    pump.set_pump_value(False)

for pump in pumps:
    pump.set_pump_value(True)
    time.sleep(2)
    pump.set_pump_value(False)