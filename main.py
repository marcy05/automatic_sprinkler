import machine
import utime
###############################################################################
#                               CLASSES
###############################################################################

class TimeHandler:
    """
    Class to handle the time difference using the utime class and initializing the current time based on the localtime() function
    """
    def __init__(self):
        self.init_t = 0
        self.year = 0
        self.month = 0
        self.day = 0
        self.hour = 0
        self.minute = 0
        self.second = 0
        self.weekday = 0
        self.yearday = 0
        self.diff_d = 0
        self.diff_m = 0
        self.diff_h = 0
        self.diff_s = 0
        
    def get_time(self):
        return "{}:{}:{}".format(self.hour, self.minute, self.second)
    
    def initialize(self, current_time: tuple):
        if len(current_time) == 8:
            self.init_t = current_time
            self.year = self.init_t[0]
            self.month = self.init_t[1]
            self.day = self.init_t[2]
            self.hour = self.init_t[3]
            self.minute = self.init_t[4]
            self.second = self.init_t[5]
            self.weekday = self.init_t[6]
            self.yearday = self.init_t[7]
        else:
            print("Not possible to parse the current time")
    
    def print(self):
        print("{}:{}:{}".format(self.day, self.minute, self.hour))
    
    def get_diff(self):
        return "{} - {}:{}:{}".format(self.diff_d, self.diff_h, self.diff_m, self.diff_s)

    def diff_day(self, comparison:TimeHandler):
        self.diff_d = 0
        self.diff_m = 0
        self.diff_h = 0
        self.diff_s = 0
        
        MIN_IN_S = 60
        HOUR_IN_S = 3600
        DAY_IN_S = 86400

        total_seconds = self.second + self.minute*MIN_IN_S + self.hour*HOUR_IN_S + self.day*DAY_IN_S
        comp_tot_sec = comparison.second + comparison.minute*MIN_IN_S + comparison.hour*HOUR_IN_S + comparison.day*DAY_IN_S

        diff = comp_tot_sec - total_seconds

        if diff >= 0:
            if diff >= DAY_IN_S:
                if diff == DAY_IN_S:
                    self.diff_d = 1
                else:
                    self.diff_d = int(diff // DAY_IN_S)
                    remaining_seconds_for_h_conversion = diff - self.diff_d * DAY_IN_S
                    self.diff_h = int(remaining_seconds_for_h_conversion//HOUR_IN_S)
                    remaining_seconds_for_min_conversion = remaining_seconds_for_h_conversion - self.diff_h*HOUR_IN_S
                    self.diff_m = int(remaining_seconds_for_min_conversion // MIN_IN_S)
                    self.diff_s = int(remaining_seconds_for_min_conversion - self.diff_m * MIN_IN_S)
                    
            else:
                if diff >= HOUR_IN_S:
                    if diff == HOUR_IN_S:
                        self.diff_h = 1
                    else:
                        self.diff_h = int(diff // HOUR_IN_S)
                        rem_sec_for_min = diff - self.diff_h * HOUR_IN_S

                        if rem_sec_for_min >= MIN_IN_S:
                            if rem_sec_for_min == MIN_IN_S:
                                self.diff_m = 1
                            else:
                                self.diff_m = int(rem_sec_for_min // MIN_IN_S)
                                self.diff_m.second = int(rem_sec_for_min - self.diff_m * MIN_IN_S)
                        else:
                            self.diff_s = diff
                else:
                    if diff >= MIN_IN_S:
                        if diff == MIN_IN_S:
                            self.diff_m = 1
                        else:
                            self.diff_m = int(diff//MIN_IN_S)
                            self.diff_s = diff - self.diff_m*MIN_IN_S

                    else:
                        if diff > 0:
                            self.diff_s = diff
        else:
            raise ValueError("Seconds have to be a positive number")
    
    def is_passed_max_days(self, current_time: TimeHandler, max_days: int):
        if current_time.day - self.day >= max_days:
            print("START: {}".format(self.init_t))
            print("Current: {}".format(current_time.init_t))
            return True
        return False

    def is_passed_max_min(self, current_time: TimeHandler, max_min: int):
        if current_time.minute - self.minute >= max_min:
            print("START: {}".format(self.init_t))
            print("Current: {}".format(current_time.init_t))
            return True
        return False


###############################################################################
#                               GLOBAL VARIABLES
###############################################################################

# Reference utime.localtime() returns (2022, 9, 4, 19, 40, 5, 6, 247) https://docs.micropython.org/en/v1.15/library/utime.html

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

a_s0 = machine.Pin(21, machine.Pin.OUT)
a_s1 = machine.Pin(20, machine.Pin.OUT)
a_s2 = machine.Pin(19, machine.Pin.OUT)
a_s3 = machine.Pin(18, machine.Pin.OUT)
a_sig = machine.ADC(machine.Pin(26))

d_s0 = machine.Pin(10, machine.Pin.OUT)
d_s1 = machine.Pin(11, machine.Pin.OUT)
d_s2 = machine.Pin(12, machine.Pin.OUT)
d_s3 = machine.Pin(13, machine.Pin.OUT)
d_sig = machine.Pin(15, machine.Pin.OUT)

IRRIGATION_TIMER = 5 # seconds

MAXIMUM_DIGITAL_CHANNELS = 7

START_TIME = TimeHandler()
CURRENT_TIME = TimeHandler()

DAYS_UP2WATER = 1

###############################################################################
#                               FUNCTIONS
###############################################################################

def init_mux_digital():
    for channel in range(len(multiplex_selector)):
        d_s0.value(multiplex_selector[channel][0])
        d_s1.value(multiplex_selector[channel][1])
        d_s2.value(multiplex_selector[channel][2])
        d_s3.value(multiplex_selector[channel][3])
        d_sig.value(False)

def init_mux_analog():
    for channel in range(len(multiplex_selector)):
        a_s0.value(multiplex_selector[channel][0])
        a_s1.value(multiplex_selector[channel][1])
        a_s2.value(multiplex_selector[channel][2])
        a_s3.value(multiplex_selector[channel][3])
        #a_sig.value(False) #ADC objects has no attribute 'value'
    
def init_global_variables():
    global START_TIME, CURRENT_TIME
    START_TIME = TimeHandler()
    START_TIME.initialize(utime.localtime())

    CURRENT_TIME = TimeHandler()
    CURRENT_TIME.initialize(utime.localtime())

def init():
    init_mux_digital()
    #init_mux_analog() # no needs since it is used for analog and does not persist values in the value method
    init_global_variables()


def relais_setter(channel: int, signal: bool):
    global d_s0, d_s1, d_s2, d_s3

    if channel < 16:
        d_s0.value(multiplex_selector[channel][0])
        d_s1.value(multiplex_selector[channel][1])
        d_s2.value(multiplex_selector[channel][2])
        d_s3.value(multiplex_selector[channel][3])
        print("{}".format(multiplex_selector[channel]))
        d_sig.value(signal)
    else:
        print("impossible channel selected: {}".format(channel))


def continue_to_irrigate(last_irrigation : TimeHandler):
    now = TimeHandler()
    now.initialize(utime.localtime())
    
    if last_irrigation.diff_day(now) >= IRRIGATION_TIMER:
        return True
    
    else:
        return False

    
###############################################################################
#                               MAIN LOOP
###############################################################################
init()

sem = 0

while True:
    CURRENT_TIME.initialize(utime.localtime())

    #TODO to be substituted with one day check
    if START_TIME.is_passed_max_min(CURRENT_TIME, DAYS_UP2WATER):


        for channel in range(0, MAXIMUM_DIGITAL_CHANNELS):
            print("Setting {}".format(channel))
            relais_setter(channel, True)
            utime.sleep(IRRIGATION_TIMER)
    else:
        utime.sleep(5)

        
 

