# #############################################################################
#                               IMPORT
# #############################################################################
import time
import network

import ntptime as ntp
from src.my_secret import secret
from src.simple_logger import SimpleLogger, LogLevels

# #############################################################################
#                          GLOBAL VARIABLES
# #############################################################################
logger = SimpleLogger(LogLevels.INFO)

# #############################################################################
#                               CLASSES
# #############################################################################
class BackEndInterface:
    def __init__(self) -> None:
        logger.info(f"{self.__class__.__name__} - Init Backend interface")
        self.network_status = False
        self.network_ssid = ""
        self.network_password = ""
        self.ntp_sync_done = False
        self.subscribed_tipic = "garden"

        self.wlan = network.WLAN(network.STA_IF)

        init_result = self._init_secret()

        if init_result:
            logger.debug(f"{self.__class__.__name__} - Backend interface correctly init.")
        else:
            logger.error(f"{self.__class__.__name__} - Not possible to init the Backend interface.")
        logger.debug(f"{self.__class__.__name__} - Init Backend finished.")

    def _init_secret(self) -> bool:
        try:
            self.network_ssid = secret["network_ssid"]
            self.network_password = secret["network_password"]
            return True
        except Exception:
            logger.error(f"{self.__class__.__name__} - Not possible to find secret file.")
            return False

    def init(self):
        self.connect()
        self.set_correct_time()

    def connect(self):
        logger.info(f"{self.__class__.__name__} - Connecting...")
        self.wlan.active(True)
        self.wlan.connect(self.network_ssid, self.network_password)
        max_retries = 20
        for i in range(max_retries):
            if not self.wlan.isconnected():
                logger.debug(f"{self.__class__.__name__} - Connection retry {i + 1}/{max_retries}")
                time.sleep(1)
            else:
                logger.debug(f"{self.__class__.__name__} - Connected.")
                self.network_status = True
                break
        if not self.wlan.isconnected():
            logger.error(f"{self.__class__.__name__} - Not possible to connect to internet.")

    def set_correct_time(self):
        if self.network_status:
            if self.wlan.isconnected():
                try:
                    ntp.settime()
                    self.ntp_sync_done = True
                    logger.info(f"{self.__class__.__name__} - NTP time set: {time.localtime()}")
                except Exception:
                    logger.warning(f"{self.__class__.__name__} - Not possible to set global time")
