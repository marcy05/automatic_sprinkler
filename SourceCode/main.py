# #############################################################################
#                               IMPORT
# #############################################################################

from src.garden import Garden
from src.simple_logger import logger
from src.hw_interface import HwInterface
from src.hw_interface import status_led
from src.hw_interface import status_led_ext
from src.hw_interface import status_led_wifi
from machine import reset

# #############################################################################
#                               GLOBAL VARIABLES
# #############################################################################

HwInterface().reset_digital_mux()

my_garden = Garden()
my_garden.backend.init()
my_garden.init_timers()

# #############################################################################
#                               MAIN LOOP
# #############################################################################

logger.info("Entering main loop ->")

status_led.value(1)
status_led_ext.value(1)

while True:
    answer = my_garden.run()
    if answer == "ForcedExit":
        logger.warning("Exit has been forced")
        HwInterface().reset_digital_mux()
        break
    elif answer == "SystemReset":
        logger.warning("Forced System reset")
        HwInterface().reset_digital_mux()
        status_led.value(0)
        status_led_ext.value(0)
        status_led_wifi.value(1)
        reset()

status_led.value(0)
status_led_ext.value(0)
status_led_wifi.value(1)
