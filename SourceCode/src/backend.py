# #############################################################################
#                               IMPORT
# #############################################################################
import time
import network
import json

import ntptime as ntp
from src.my_secret import secret
from src.simple_logger import logger
from src.utelegram.utelegram import Ubot
from src.utelegram.utelegram import TelegramMessage

from src.secretHandler import update_telegram_pwd
from src.secretHandler import get_telegram_pwd
from src.secretHandler import set_allowed_user
from src.secretHandler import is_user_allowed

from src.my_secret import secret

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
        self.bot.register("/register_device", self.register_device)
        self.bot.set_default_handler(self.get_message)

    def register_device(self, message) -> None:
        msg = TelegramMessage(message)
        splitted_msg = msg.msg_text.split(" ")

        if len(splitted_msg) == 2:
            user_pwd = splitted_msg[1]

            if get_telegram_pwd() == "":

                logger.info(f"A new password is going to be set to: {user_pwd}")
                update_telegram_pwd(user_pwd)
                set_allowed_user(msg.sender_id)
                logger.info(f"New password set to: {user_pwd}")
                self.bot.send(msg.chat_id, "Password set")

            elif user_pwd == get_telegram_pwd():
                set_allowed_user(msg.sender_id)
                logger.info("Password correct. New User added.")
                self.bot.send(msg.chat_id, "Password correct. New User added.")

            else:
                logger.info("ERROR: Wrong password, not possible to add new user")
                self.bot.send(msg.chat_id, "ERROR: Wrong password, not possible to add new user")
        else:
            self.bot.send(msg.chat_id, "Invalid number of argument")

    def reply_start(self, message) -> TelegramMessage:
        logger.debug("Reply start message")
        msg = TelegramMessage(message)
        start_message = "The following messages are supported:\n"\
                        "/register_device <password> - It start the paring procedure\n\n"\
                        "/get_sensors_data - Retrive Sensors data\n\n"\
                        "/get_pumps_data - Retrive Pumps data\n\n"\
                        "/set_p<pump_id(0-6)>_stat_<status(true/false)>\n\n"\
                        "/set_p<pump_id(0-6)>_actPeriod_<seconds as float>\n\n"\
                        "/set_s<sensor_id(0-6)>_stat_<status(true/false)>\n"
        self.bot.send(message['message']['chat']['id'], start_message)

        logger.debug("Start message replied.")

        return msg

    def get_message(self, message) -> TelegramMessage:
        logger.debug(f"Got message: {json.dumps(message)}")

        msg = TelegramMessage(message)

        if is_user_allowed(msg.sender_id):
            logger.info("Autorized user")
            return msg
        else:
            logger.warning("The user is not allowed to communicate befer a successful registration")
            self.bot.send(msg.chat_id, "The user is not allowed to communicate befer a successful registration")
            return None
