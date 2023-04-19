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

INFLUXDB_ADDRESS = '192.168.0.8'
INFLUXDB_USER = 'mqtt'
INFLUXDB_PASSWORD = 'mqtt'
INFLUXDB_DATABASE = 'weather_stations'

MQTT_ADDRESS = '192.168.0.8'
MQTT_USER = 'cdavid'
MQTT_PASSWORD = 'cdavid'
MQTT_TOPIC = 'home/+/+'
MQTT_REGEX = 'home/([^/]+)/([^/]+)'
MQTT_CLIENT_ID = 'MQTTInfluxDBBridge'


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


def main():
    _init_indluxdb_database()


if __name__ == "__main__":
    main()
