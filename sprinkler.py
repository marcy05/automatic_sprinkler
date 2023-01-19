import machine
import utime
###############################################################################
#                               CLASSES
###############################################################################

class TimeHandler:
    """
    Class to handle the time difference using the utime class and initializing the current time based on the localtime() function.

    Reference utime.localtime() returns (2022, 9, 4, 19, 40, 5, 6, 247) (year, month, mday, hour, minute, second, weekday, yearday)
    https://docs.micropython.org/en/v1.15/library/utime.html
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
        """ get_time() -> string, 'h:m:s'"""
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
        """ print() -> string, 'day:h:min'"""
        print("{}:{}:{}".format(self.day, self.hour, self.minute))
    
    def get_diff(self):
        """ get_diff() -> string, 'diff - h:min:s'"""
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
        """is_passed_max_days(...) -> bool 
        
            Arguments:
                current_time: TimeHandler, time to be checked against
                max_days: int, maximum days to be compared with
        """
        if current_time.day - self.day >= max_days:
            logger.info("{}day(s) passed. Start time: {}; Current time: {}".format(max_days, self.init_t, current_time.init_t))
            logger.debug("START: {}".format(self.init_t))
            logger.debug("Current: {}".format(current_time.init_t))
            return True
        return False

    def is_passed_max_hours(self, current_time: TimeHandler, max_hour: int):
        """is_passed_max_hours(...) -> bool 
        
            Arguments:
                current_time: TimeHandler, time to be checked against
                max_hour: int, maximum hours to be compared with
        """
        if current_time.hour - self.hour >= max_hour:
            logger.info("{}h passed. Start time: {}; Current time: {}".format(max_hour, self.init_t, current_time.init_t))
            return True
        return False

    def is_passed_max_min(self, current_time: TimeHandler, max_min: int):
        """is_passed_max_min(...) -> bool 
        
            Arguments:
                current_time: TimeHandler, time to be checked against
                max_min: int, maximum minutes to be compared with
        """
        if current_time.minute - self.minute >= max_min:
            logger.info("{}min passed. Start time: {}; Current time: {}".format(max_min, self.init_t, current_time.init_t))
            return True
        return False

    def is_daytime(self):
        """is_datetime() -> bool

            Returns:
                True: if 8 < hour < 19
                False: in all other cases
        """
        if self.hour > 8 and self.hour < 19:
            return True
        else:
            return False

###############################################################################
#                               LOGGING
###############################################################################

class SimpleLogger:
    """Class to handle logging events"""
    def __init__(self, file_name = None, log2file: bool = False, log2console: bool = True,
                    min_log_level: int = 0):
        self.message = ""
        self.file_name = file_name
        self.log2file = log2file
        self.log2console = log2console
        self.log_level = min_log_level

    def new_start(self):
        message = "="*50
        message += "{}".format(utime.localtime())
        message += "="*50

        if self.log2console:
            print(message)

        if self.log2file:
            if self.file_name is not None:
                with open(self.file_name, 'a') as fw:
                    fw.write("DEBUG: {}\n".format(message))
            else:
                print("Warn: seems that you are willing to log to file but filename is missing.")


    def debug(self, message: str):
        if self.log_level == 0 or self.log_level <= 10:

            if self.log2console:
                print("DEBUG: {}".format(message))

            if self.log2file:
                if self.file_name is not None:
                    with open(self.file_name, 'a') as fw:
                        fw.write("DEBUG: {}\n".format(message))

    def info(self, message: str):
        if self.log_level == 0 or self.log_level <= 20:
            if self.log2console:
                print("INFO: {}".format(message))
            
            if self.log2file:
                if self.file_name is not None:
                    with open(self.file_name, 'a') as fw:
                        fw.write("INFO: {}\n".format(message))

    def warning(self, message: str):
        if self.log_level == 0 or self.log_level <= 30:
            if self.log2console:
                print("WARNING: {}".format(message))

            if self.log2file:
                if self.file_name is not None:
                    with open(self.file_name, 'a') as fw:
                        fw.write("WARNING: {}\n".format(message))

    def error(self, message: str):
        if self.log_level == 0 or self.log_level <= 40:
            if self.log2console:
                print("ERROR: {}".format(message))
            
            if self.log2file:
                if self.file_name is not None:
                    with open(self.file_name, 'a') as fw:
                        fw.write("ERROR: {}\n".format(message))

    def critical(self, message: str):
        if self.log_level == 0 or self.log_level <= 10:
            if self.log2console:
                print("CRITICAL: {}".format(message))

            if self.log2file:
                if self.file_name is not None:
                    with open(self.file_name, 'a') as fw:
                        fw.write("CRITICAL: {}\n".format(message))


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

#########   IRRIGATION RELATED VARIABLES
IRRIGATION_TIMER = 7 # seconds almost a glass of water
IRRIGATION_LOOPS = 2

######### TIME HANDLING VARIABLES

START_TIME = TimeHandler()  # Reference time from when start to count, updated every time the relais are activated.
CURRENT_TIME = TimeHandler()

DAYS_UP2WATER = 6   # How frequently the relais should be activated to turn on the pumps

logger = SimpleLogger(file_name="execution.log")

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
    
def init_global_variables():
    global START_TIME, CURRENT_TIME
    START_TIME = TimeHandler()
    START_TIME.initialize(utime.localtime())

    CURRENT_TIME = TimeHandler()
    CURRENT_TIME.initialize(utime.localtime())

def init():
    logger.new_start()
    init_mux_digital()
    init_global_variables()
    switch_off_all_relais()


def relais_setter(channel: int, signal: bool):
    global d_s0, d_s1, d_s2, d_s3

    if channel < 16:
        d_s0.value(multiplex_selector[channel][0])
        d_s1.value(multiplex_selector[channel][1])
        d_s2.value(multiplex_selector[channel][2])
        d_s3.value(multiplex_selector[channel][3])
        d_sig.value(signal)
    else:
        logger.critical("impossible channel selected: {}".format(channel))


def continue_to_irrigate(last_irrigation : TimeHandler):
    now = TimeHandler()
    now.initialize(utime.localtime())
    
    if last_irrigation.diff_day(now) >= IRRIGATION_TIMER:
        return True
    
    else:
        return False

def reset_start_time():
    global START_TIME
    now = utime.localtime()
    logger.info("START_TIME reset to: {}".format(now))
    START_TIME.initialize(now)

def switch_off_all_relais():
    for channel in range(len(multiplex_selector)):
        d_s0.value(multiplex_selector[channel][0])
        d_s1.value(multiplex_selector[channel][1])
        d_s2.value(multiplex_selector[channel][2])
        d_s3.value(multiplex_selector[channel][3])
        d_sig.value(False)
    logger.info("Reset all channels")
    
###############################################################################
#                               MAIN LOOP
###############################################################################
init()

sem = 0

while True:
    CURRENT_TIME.initialize(utime.localtime())

    if CURRENT_TIME.is_daytime():

        if is_water_sensor_present():

            if is_plant_dry():
                pass
                # activate the pumps
            else:
                pass
                # log plants still wet
        else:
            START_TIME.is_passed_max_hours(CURRENT_TIME, DAYS_UP2WATER)
            # activate the pumps


    # #TODO to be substituted with one day check
    # if START_TIME.is_passed_max_hours(CURRENT_TIME, DAYS_UP2WATER):
    # #if True:
    #     print("Running")

    #     for loop in range(0, IRRIGATION_LOOPS):
    #         logger.debug("Irrigation loop: {}".format(loop))
    #         for channel in range(0, MAXIMUM_DIGITAL_CHANNELS):
    #             logger.info("Activated relay {}. Water will be active for: {}".format(channel, IRRIGATION_TIMER))
    #             relais_setter(channel, True)
    #             utime.sleep(IRRIGATION_TIMER)
    #         switch_off_all_relais()

    #     reset_start_time()

    # else:
    #     utime.sleep(SYS_UPDATE_PERIOD)

