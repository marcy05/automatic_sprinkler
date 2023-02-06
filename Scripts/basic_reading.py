import machine
import utime

###############################################################################
#                               GLOBAL VARIABLES
###############################################################################

#########   SYSTEM VARIABLES
SYS_UPDATE_PERIOD = 5

#########   MUX RELATED VARIABLES
multiplex_selector = [(0,0,0,0),
                      (1,0,0,0),
                      (0,1,0,0),
                      (1,1,0,0),
                      (0,0,1,0),
                      (1,0,1,0),
                      (0,1,1,0),
                      (1,1,1,0),
                      (0,0,0,1),
                      (1,0,0,1),
                      (0,1,0,1),
                      (1,1,0,1),
                      (0,0,1,1),
                      (1,0,1,1),
                      (0,1,1,1),
                      (1,1,1,1)]

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
a_sig = machine.ADC(machine.Pin(SENSOR_SIG))

d_s0 = machine.Pin(PUMP_S0, machine.Pin.OUT)
d_s1 = machine.Pin(PUMP_S1, machine.Pin.OUT)
d_s2 = machine.Pin(PUMP_S2, machine.Pin.OUT)
d_s3 = machine.Pin(PUMP_S3, machine.Pin.OUT)
d_sig = machine.Pin(PUMP_SIG, machine.Pin.OUT)

# Set it to 16 if all channels are used.
MAXIMUM_DIGITAL_CHANNELS = 7

#Calibraton values
min_moisture=19200
max_moisture=49300

def get_analog_read(sensor: int):
    a_s0.value(multiplex_selector[sensor][0])
    a_s1.value(multiplex_selector[sensor][1])
    a_s2.value(multiplex_selector[sensor][2])
    a_s3.value(multiplex_selector[sensor][3])
    
    return a_sig.read_u16()


def main():
    """
    Read the values from all sensors, put in in a list and print them all together.
    """
    counter = 0
    while True:
        counter += 1
        sensors_value = []
        for i in range(0, MAXIMUM_DIGITAL_CHANNELS):
            sensors_value.append(int(get_analog_read(i)))
        print("Run: {}\nS0: {}\nS1: {}\nS2: {}\nS3: {}\nS4: {}\nS5: {}\nS6: {}\n".format(counter, sensors_value[0],
                                                                                         sensors_value[1],
                                                                                         sensors_value[2],
                                                                                         sensors_value[3],
                                                                                         sensors_value[4],
                                                                                         sensors_value[5],
                                                                                         sensors_value[6]))
        utime.sleep(2)


def main1():
    """
    Read from GPIO 26.
    """

    read_analog = machine.ADC(26)
    
    counter = 0
    while True:
        counter += 1
        print("Reading {}: {}".format(counter, read_analog.read_u16()))
        utime.sleep(2)

def main2():
    """
    Read from multiplexer the CONSIDERED_SENSOR.
    """
    SENSOR_SIG = 26
    SENSOR_S3 = 18
    SENSOR_S2 = 19
    SENSOR_S1 = 20
    SENSOR_S0 = 21

    CONSIDERED_SENSOR = 0

    a_s0 = machine.Pin(SENSOR_S0, machine.Pin.OUT)
    a_s1 = machine.Pin(SENSOR_S1, machine.Pin.OUT)
    a_s2 = machine.Pin(SENSOR_S2, machine.Pin.OUT)
    a_s3 = machine.Pin(SENSOR_S3, machine.Pin.OUT)
    a_sig = machine.ADC(SENSOR_SIG)

    a_s0.value(multiplex_selector[CONSIDERED_SENSOR][0])
    a_s1.value(multiplex_selector[CONSIDERED_SENSOR][1])
    a_s2.value(multiplex_selector[CONSIDERED_SENSOR][2])
    a_s3.value(multiplex_selector[CONSIDERED_SENSOR][3])
    
    counter = 0
    while True:
        counter += 1
        print("Reading {}: {}".format(counter, a_sig.read_u16()))
        utime.sleep(2)

main()