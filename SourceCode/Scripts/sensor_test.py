import utime
import machine


###############################################################################
#                               GLOBAL VARIABLES
###############################################################################

class Sensor:
    def __init__(self) -> None:
        self.min: float = 0  # Volts
        self.max: float = 3.3  # Volts
        self.average: float = 0
        self.percentage: int = 0
        self.average_buffer = []
        self.current_value: int = 0

        self.DRY_THRESHOLD_PERC = 88
        self.GROUNDED_THRESHOLD_PERC = 1
        self.MEASURING_MIN_PERC = 40
        self.MEASURING_MAX_PERC = 88
    
    def get_average(self):
        sum = 0
        if len(self.average_buffer) > 0:
            for i in self.average_buffer:
                sum += i
            return sum / len(self.average_buffer)
        else:
            return 0

    def clean_circular_buffer(self):
        self.average_buffer.pop(0)

    def update_average(self):
        if len(self.average_buffer) < 10:
            self.average_buffer.append(self.current_value)
            self.average = self.get_average()
        elif len(self.average_buffer) >= 10:
            self.clean_circular_buffer()
            self.average_buffer.append(self.current_value)
            self.average = self.get_average()

    def update_percentage(self):
        if self.max != 0 and self.max > self.min:
            self.percentage = 100 - int((self.max - self.current_value) * 100 / (self.max - self.min))
        else:
            self.percentage = 0

    def add_sensor_values(self, current_value: int):
        self.current_value = current_value
        self.update_average()
        self.update_percentage()

    def get_info(self):
        if self.percentage >= self.DRY_THRESHOLD_PERC:
            return "MIN: {}, MAX: {}, AVERAGE: {}, %: {}, READ: {} -->" \
            " Dry or sensor out of water.".format(self.min,
                                                  self.max,
                                                  self.average,
                                                  self.percentage,
                                                  self.current_value)
        elif self.current_value < self.GROUNDED_THRESHOLD_PERC:
            return "MIN: {}, MAX: {}, AVERAGE: {}, %: {}, READ: {} -->" \
            " Grounded sensor".format(self.min,
                                      self.max,
                                      self.average,
                                      self.percentage,
                                      self.current_value)
        elif self.percentage > self.MEASURING_MIN_PERC and self.percentage < self.MEASURING_MAX_PERC:
            return "MIN: {}, MAX: {}, AVERAGE: {}, %: {}, READ: {} -->" \
            " [?] Measuring or not connected.".format(self.min,
                                                      self.max,
                                                      self.average,
                                                      self.percentage,
                                                      self.current_value)
        else:
            return "MIN: {}, MAX: {}, AVERAGE: {}, %: {}, READ: {} -->" \
            " [?] Check".format(self.min,
                                self.max,
                                self.average,
                                self.percentage,
                                self.current_value)


# #######   SYSTEM VARIABLES
SYS_UPDATE_PERIOD = 5

# #######   MUX RELATED VARIABLES
multiplex_selector = [(0, 0, 0, 0),
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

# the multiplexer will be controlled by s0, s1, s2, s3 and the prefix "a_" will refer to the analog
#   and "d_" will refer to the digital

PUMP_SIG = 10
PUMP_S3 = 11
PUMP_S2 = 12
PUMP_S1 = 13
PUMP_S0 = 15

SENSOR_SIG = 26
SENSOR_S3 = 18
SENSOR_S2 = 19
SENSOR_S1 = 20
SENSOR_S0 = 21

a_s0 = machine.Pin(SENSOR_S0, machine.Pin.OUT)
a_s1 = machine.Pin(SENSOR_S1, machine.Pin.OUT)
a_s2 = machine.Pin(SENSOR_S2, machine.Pin.OUT)
a_s3 = machine.Pin(SENSOR_S3, machine.Pin.OUT)
# a_sig = machine.ADC(machine.Pin(SENSOR_SIG))
a_sig = machine.ADC(SENSOR_SIG)

d_s0 = machine.Pin(PUMP_S0, machine.Pin.OUT)
d_s1 = machine.Pin(PUMP_S1, machine.Pin.OUT)
d_s2 = machine.Pin(PUMP_S2, machine.Pin.OUT)
d_s3 = machine.Pin(PUMP_S3, machine.Pin.OUT)
d_sig = machine.Pin(PUMP_SIG, machine.Pin.OUT)

# Set it to 16 if all channels are used.
MAXIMUM_DIGITAL_CHANNELS = 7


def get_analog_read(sensor: int):
    utime.sleep(.1)
    a_s0.value(multiplex_selector[sensor][0])
    a_s1.value(multiplex_selector[sensor][1])
    a_s2.value(multiplex_selector[sensor][2])
    a_s3.value(multiplex_selector[sensor][3])
    volt = a_sig.read_u16() * 3.3 / 65535

    return volt


def main():
    """
    Read from all sensor via multiplexer and print via get_info method which return
        if the sensor is connected, grounded or unknown.
    """
    counter = 0

    sensor_dic = {}

    while True:
        for i in range(0, MAXIMUM_DIGITAL_CHANNELS):
            if str(i) not in sensor_dic:
                temp = Sensor()
                temp.add_sensor_values(get_analog_read(i))
                sensor_dic[str(i)] = temp
            else:
                sensor_dic[str(i)].add_sensor_values(get_analog_read(i))
            utime.sleep(.1)

        print("Run: {}".format(counter))

        for i in range(0, len(sensor_dic)):
            print("S{}: {}".format(str(i), sensor_dic[str(i)].get_info()))

        counter += 1
        utime.sleep(.5)


def main2():
    """
    Test if the sensors are reading correctly based on thresholds.
    """
    considered_sensor = 6

    WET_REF = 1.8
    DRY_REF = 2.8
    NO_SENSOR = 1

    while True:
        detected_value = get_analog_read(considered_sensor)
        if detected_value <= WET_REF and detected_value > NO_SENSOR:
            print("Stop pump. I'm wet: {}".format(detected_value))
        elif detected_value >= DRY_REF:
            print("Activate the pump, I'm dry: {}".format(detected_value))
        elif detected_value < 1:
            print("Sensor not active: {}".format(detected_value))
        else:
            print("Wait for water: {}".format(detected_value))

        utime.sleep(1)


def main3():
    """
    Test the conversion from digital read to volt.

    The conversion is based on 16bit sensor and 3.3V
    """

    sensor = 0
    a_s0.value(multiplex_selector[sensor][0])
    a_s1.value(multiplex_selector[sensor][1])
    a_s2.value(multiplex_selector[sensor][2])
    a_s3.value(multiplex_selector[sensor][3])

    while True:
        volt = a_sig.read_u16() * 3.3 / 65535
        print(volt)
        utime.sleep(.3)


main()
