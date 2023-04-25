import re
import sys
import json
import logging
import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

INFLUXDB_ADDRESS = ''
INFLUXDB_USER = ''
INFLUXDB_PASSWORD = ''
INFLUXDB_DATABASE = ''

MQTT_ADDRESS = ''
MQTT_USER = ''
MQTT_PASSWORD = ''
MQTT_TOPIC = ''
MQTT_REGEX = ''
MQTT_CLIENT_ID = ''


def load_credential():
    global INFLUXDB_ADDRESS, INFLUXDB_USER, INFLUXDB_PASSWORD, INFLUXDB_DATABASE
    global MQTT_ADDRESS, MQTT_USER, MQTT_PASSWORD, MQTT_TOPIC, MQTT_REGEX, MQTT_CLIENT_ID

    with open("secret.json", 'r') as f:
        fj = json.load(f)
        INFLUXDB_ADDRESS = fj["influxdb_address"]
        INFLUXDB_USER = fj["influxdb_user"]
        INFLUXDB_PASSWORD = fj["influxdb_password"]
        INFLUXDB_DATABASE = fj["influxdb_db"]

        MQTT_ADDRESS = fj["mqtt_address"]
        MQTT_USER = fj["mqtt_user"]
        MQTT_PASSWORD = fj["mqtt_password"]
        MQTT_TOPIC = fj["mqtt_topic"]
        MQTT_REGEX = fj["mqtt_regex"]
        MQTT_CLIENT_ID = fj["mqtt_client_id"]

        logger.debug("paramenters:\nINFLUXDB_ADDRESS = {}\n"
              	     "INFLUXDB_USER = {}\n INFLUXDB_PASSWORD = {}\n"
                     "INFLUXDB_DATABASE = {}\n\n MQTT_ADDRESS = {}\n"
                     "MQTT_USER = {}\n MQTT_PASSWORD = {}\n"
                     "MQTT_TOPIC = {}\n"
                     "MQTT_REGEX = {}\n"
                     "MQTT_CLIENT_ID = {}".format(INFLUXDB_ADDRESS,
                                                  INFLUXDB_USER,
                                                  INFLUXDB_PASSWORD,
                                                  INFLUXDB_DATABASE,
                                                  MQTT_ADDRESS,
                                                  MQTT_USER,
                                                  MQTT_PASSWORD,
                                                  MQTT_TOPIC,
                                                  MQTT_REGEX,
                                                  MQTT_CLIENT_ID))


load_credential()
influxdb_client = InfluxDBClient(
    INFLUXDB_ADDRESS, 8086, INFLUXDB_USER, INFLUXDB_PASSWORD, None)


def _init_indluxdb_database():
    database = influxdb_client.get_list_database()
    if len(list(filter(lambda x: x['name'] == INFLUXDB_DATABASE, database))) == 0:
        logger.debug("Database not found, it will be created")
        influxdb_client.create_database(INFLUXDB_DATABASE)
        logger.debug("Database created")
    influxdb_client.switch_database(INFLUXDB_DATABASE)
    logger.info("Database activated")


def on_connect(client, userdata, flags, rc):
    status={"0":"successful", "1":"refused-Incorrect protocol version", 
            "2":"refused-Invalid client identifier", "3":"refused-server unavailable", 
            "4":"refused-Bad User or Password", "5":"refused-Not authorised"}
    logger.info("Connected with result code: {}".format(status[str(rc)]))

def on_message(client, userdata, msg):
    logger.debug("Received message...")
    logger.debug(msg.topic + " " + str(msg.payload))
    logger.debug("Here the sensor data should be parsed")

def main():
    _init_indluxdb_database()
    
    mqtt_client = mqtt.Client(MQTT_CLIENT_ID)
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    logger.debug("Connection done")
    mqtt_client.on_connet = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_ADDRESS, 1883)
    # Only when connected you can correctly subscribe to topics
    mqtt_client.subscribe(MQTT_TOPIC)
    mqtt_client.loop_forever()

if __name__ == "__main__":
    main()
