# #############################################################################
#                               IMPORT
# #############################################################################
import utime
import json
import _thread

from src.garden import Garden
from src.simple_logger import SimpleLogger, LogLevels
from src.backend import BackEndInterface
from src.hw_interface import HwInterface, Sensor, Pump

# #############################################################################
#                               GLOBAL VARIABLES
# #############################################################################
logger = SimpleLogger(LogLevels.INFO)

HwInterface().reset_digital_mux()

my_garden = Garden()
my_garden.backend.init()
my_garden.init_timers()

# #############################################################################
#                               MAIN LOOP
# #############################################################################

logger.info("Entering main loop ->")
while True:
    my_garden.run()
