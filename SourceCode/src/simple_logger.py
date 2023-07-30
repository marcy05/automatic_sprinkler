# #############################################################################
#                               IMPORT
# #############################################################################
import utime

# #############################################################################
#                               CLASSES
# #############################################################################
class LogLevels:
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4

class SimpleLogger(LogLevels):
    def __init__(self, logging_level: LogLevels = LogLevels.DEBUG):
        self._allowed_values = [self.DEBUG, self.INFO, self.WARNING, self.ERROR]
        if logging_level not in self._allowed_values:
            raise ValueError(f"Wrong value, allowed: {self._allowed_values}")
        self._level = logging_level

    def debug(self, message: str):
        if self._level == self.DEBUG:
            current_time = utime.gmtime(utime.time())
            formatted_date = "{}/{}/{} - {}:{}:{}".format(current_time[0],
                                                          current_time[1],
                                                          current_time[2],
                                                          current_time[3],
                                                          current_time[4],
                                                          current_time[5])
            print("{} - DEBUG - {}".format(formatted_date, message))

    def info(self, message: str):
        if self._level <= self.INFO:
            current_time = utime.gmtime(utime.time())
            formatted_date = "{}/{}/{} - {}:{}:{}".format(current_time[0],
                                                          current_time[1],
                                                          current_time[2],
                                                          current_time[3],
                                                          current_time[4],
                                                          current_time[5])
            print("{} - INFO - {}".format(formatted_date, message))

    def warning(self, message: str):
        if self._level <= self.WARNING:
            current_time = utime.gmtime(utime.time())
            formatted_date = "{}/{}/{} - {}:{}:{}".format(current_time[0],
                                                          current_time[1],
                                                          current_time[2],
                                                          current_time[3],
                                                          current_time[4],
                                                          current_time[5])
            print("{} - WARNING - {}".format(formatted_date, message))

    def error(self, message: str):
        if self._level <= self.ERROR:
            current_time = utime.gmtime(utime.time())
            formatted_date = "{}/{}/{} - {}:{}:{}".format(current_time[0],
                                                          current_time[1],
                                                          current_time[2],
                                                          current_time[3],
                                                          current_time[4],
                                                          current_time[5])
            print("{} - ERROR - {}".format(formatted_date, message))
