# #############################################################################
#                               IMPORT
# #############################################################################
import time
import network

import ntptime as ntp
from src.my_secret import secret
from src.simple_logger import logger
from src.utelegram.utelegram import Ubot
from src.utelegram.utelegram import TelegramMessage

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
        self.init_bot()

    def connect(self):
        logger.info(f"{self.__class__.__name__} - Connecting...")
        self.wlan.active(True)
        self.wlan.connect(self.network_ssid, self.network_password)
        max_retries = 20
        for i in range(max_retries):
            if not self.wlan.isconnected():
                logger.info(f"{self.__class__.__name__} - Connection retry {i + 1}/{max_retries}")
                time.sleep(1)
            else:
                logger.info(f"{self.__class__.__name__} - Connected.")
                self.network_status = True
                break
        if not self.wlan.isconnected():
            logger.error(f"{self.__class__.__name__} - Not possible to connect to internet.")

    def set_correct_time(self):
        if self.network_status:
            if self.wlan.isconnected():
                try:
                    logger.info("Setting global time...")
                    ntp.settime()
                    self.ntp_sync_done = True
                    _current_time = time.localtime()
                    _year = _current_time[0]
                    _month = _current_time[1]
                    _day = _current_time[2]
                    _hour = _current_time[3]
                    _min = _current_time[4]
                    _sec = _current_time[5]

                    logger.info(f"{self.__class__.__name__} - NTP time set: {_day}/{_month}/{_year} {_hour}:{_min}:{_sec}")
                except Exception:
                    logger.warning(f"{self.__class__.__name__} - Not possible to set global time")

    def init_bot(self):
        self.bot = Ubot(secret["token"])

        self.bot.register("/start", self.reply_start)
        self.bot.set_default_handler(self.get_message)

    def reply_start(self, message) -> TelegramMessage:
        logger.debug("Reply start message")
        msg = TelegramMessage(message)
        start_message = "The following messages are supported:\n"\
                        "/ping - It will answer pong\n\n"\
                        "/get_sensors_data - Retrive Sensors data\n\n"\
                        "/get_pumps_data - Retrive Pumps data\n\n"\
                        "/set_p<pump_id(0-6)>_stat_<status(true/false)>\n\n"\
                        "/set_p<pump_id(0-6)>_actPeriod_<seconds as float>\n\n"\
                        "/set_s<sensor_id(0-6)>_stat_<status(true/false)>\n"
        self.bot.send(message['message']['chat']['id'], start_message)

        logger.debug("Start message replied.")

        return msg

    def get_message(self, message) -> TelegramMessage:
        logger.debug("Getting default message")

        msg = TelegramMessage(message)
        return msg
