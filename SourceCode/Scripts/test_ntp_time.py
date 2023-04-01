import time
import utime
# import my_ntp
import network
from my_secret import secret
from umqtt.simple import MQTTClient


##########################################################################
import utime

try:
    import usocket as socket
except:
    import socket
try:
    import ustruct as struct
except:
    import struct

# The NTP host can be configured at runtime by doing: ntptime.host = 'myhost.org'
host = "pool.ntp.org"
# The NTP socket timeout can be configured at runtime by doing: ntptime.timeout = 2
timeout = 5

class Ntp:
    def time(self):
        NTP_QUERY = bytearray(48)
        NTP_QUERY[0] = 0x1B
        addr = socket.getaddrinfo(host, 123)[0][-1]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.settimeout(timeout)
            res = s.sendto(NTP_QUERY, addr)
            msg = s.recv(48)
            print("Message recevied: {}".format(msg))
        finally:
            s.close()
        val = struct.unpack("!I", msg[40:44])[0]
        print("Get valie: {}".format(val))
        EPOCH_YEAR = utime.gmtime(0)[0]
        print("Year: {}".format(utime.gmtime(0)))
        if EPOCH_YEAR == 2000:
            # (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
            NTP_DELTA = 3155673600
        elif EPOCH_YEAR == 1970:
            # (date(1970, 1, 1) - date(1900, 1, 1)).days * 24*60*60
            NTP_DELTA = 2208988800
        else:
            raise Exception("Unsupported epoch: {}".format(EPOCH_YEAR))
        print("Final time: {}".format(val - NTP_DELTA))
        return val - NTP_DELTA


    # Time zone is supported. Counting starts from UTC time.
    def settime(self, h_shift: int = 0):
        print("Getting time")
        t = self.time()
        print("Time correctly obtained")
        import machine

        tm = utime.gmtime(t)
        zone_t = t + h_shift*60*60
        tm = utime.gmtime(zone_t)
        machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))
        print("Time correctly set")
###########################################################################

class Log:
    def debug(self, message):
        print("DEBUG: {}".format(message))

    def info(self, message):
        print("INFO: {}".format(message))

    def warning(self, message):
        print("WARNING: {}".format(message))
    
    def error(self, message):
        print("ERROR: {}".format(message))

logger = Log()

class BackEndInterface:
    def __init__(self) -> None:
        logger.debug("Init Backend interface")
        self.network_ssid = ""
        self.network_password = ""
        self.mqtt_server_ip = ""
        self.client_id = ""
        self.user_raspberry = ""
        self.pass_rasberry = ""
        self.mqtt_client = MQTTClient
        self.mqtt_status = False
        self.subscribed_tipic = "garden"

        self.wlan = network.WLAN(network.STA_IF)

        init_result = self._init_secret()

        if init_result:
            logger.debug("Backend interface correctly init.")
        else:
            logger.error("Not possible to init the Backend interface.")
        logger.debug("Init Backend finished.")

    def _init_secret(self) -> bool:
        try:
            self.network_ssid = secret["network_ssid"]
            self.network_password = secret["network_password"]
            self.mqtt_server_ip = secret["mqtt_server_ip"]
            self.client_id = secret["client_id"]
            self.user_raspberry = secret["user_raspberry"]
            self.pass_rasberry = secret["pass_rasberry"]
            return True
        except:
            logger.error("Not possible to find secret file.")
            return False

    def connect(self):
        logger.debug("Connecting...")
        self.wlan.active(True)
        self.wlan.connect(self.network_ssid, self.network_password)
        max_retries = 20
        for i in range(max_retries):
            if not self.wlan.isconnected():
                logger.debug("Connection retry {}/{}".format(i+1, max_retries))
                utime.sleep(1)
            else:
                logger.debug("Connected.")
                break
        if not self.wlan.isconnected():
            logger.error("Not possible to connect to internet.")

    def set_correct_time(self):
        if self.wlan.isconnected():
            try:
                ntp = Ntp()
                ntp.settime()
                print("Set time correctly executed\nPrinting...")
                # my_ntp.settime(1)
                logger.debug("NTP time: {}".format(time.localtime()))
                #logger.debug("NTP time set: {}".format(time.locatime()))
            except:
                logger.warning("Not possible to set global time")



backend = BackEndInterface()
backend.connect()
print("Current time: {}".format(time.localtime()))
backend.set_correct_time()
print("Current time after set: {}".format(time.localtime()))
