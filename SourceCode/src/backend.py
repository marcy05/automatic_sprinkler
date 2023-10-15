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
        self.bot.register("/am_I_alive", self.alive_msg)
        self.bot.register("/get_system_time", self.get_sys_time)
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
        start_message = "The following messages are supported.\n" + \
                        "General commands:\n" + \
                        "/am_I_alive - Return if the system is active\n" + \
                        "/get_system_time - Return the system time\n" + \
                        "/register_device <password> - It start the paring procedure\n" + \
                        "/force_watering_cycle - It start a watering cycle\n" + \
                        "/get_sensors_data - Retrive Sensors data\n" + \
                        "/get_pumps_data - Retrive Pumps data\n" + \
                        "/get_garden_timers - Retrive general garden timers\n" + \
                        "/get_garden_pumpActiveStatus - Retrive garden pumps active status\n\n" + \
                        "\n" + \
                        "Settings commands:\n" + \
                        "/set_p<pump_id options: (0-6)>_stat_<option: on/off> - Manually switch a pump on and off\n\n" + \
                        "/set_p<pump_id options: (0-6)>_actPeriod_<seconds as float> - It set pump activation time during watering cycle\n\n" + \
                        "/set_p<pump_id options: (0-6)>_active_<option: on/off> - It activate or deactivate a pump during watering cycle\n\n" + \
                        "/set_s<sensor_id options: (0-6)>_stat_<option: on/off> - It activate or deactivate a sensor\n" + \
                        "/set_garden_wateringIterations_<iteration number> - It set the number of cycles the pumps will execute during watering\n" + \
                        "/set_garden_waterIterDelay_<seconds as float> - It set the delay between the cycles during watering cycle\n" + \
                        "/set_garden_sensorReadingPeriod_<seconds as float> - It set how frequently the sensors will be read\n" + \
                        "/set_backend_syncPeriod_<seconds as float> - It set how frequently the user can interact with telegram\n"

        self.bot.send(msg.chat_id, start_message)

        logger.debug("Start message replied.")

        return msg

    def alive_msg(self, message):
        logger.debug("Alive message request reply")
        msg = TelegramMessage(message)
        self.bot.send(msg.chat_id, "The system is alive")

    def get_sys_time(self, message):
        logger.debug("Return system time request")
        _current_time = time.localtime()
        _year = _current_time[0]
        _month = _current_time[1]
        _day = _current_time[2]
        _hour = _current_time[3]
        _min = _current_time[4]
        _sec = _current_time[5]
        message_time = f"{_day:02}/{_month:02}/{_year} {_hour:02}:{_min:02}:{_sec:02}"

        msg = TelegramMessage(message)
        self.bot.send(msg.chat_id, message_time)

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
