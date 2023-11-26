import time
import json
import logging
from logging.handlers import TimedRotatingFileHandler
import os
from w1thermsensor import W1ThermSensor
import paho.mqtt.client as mqtt

# MQTT Event Handlers
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT Broker!")
    else:
        logging.error(f"Failed to connect, return code {rc}")

def on_disconnect(client, userdata, rc):
    logging.warning("Disconnected from MQTT Broker")
    # Try reconnect
    if rc != 0:  # rc = 0 means disconnect was planned
        logging.info("Attempting to reconnect to MQTT Broker")
        try:
            client.reconnect()
        except Exception as e:
            logging.error(f"Reconnection to MQTT Broker failed: {e}")

def on_publish(client, userdata, mid):
    logging.info(f"Message {mid} published")

# Load configuration from a JSON file
with open('/apps/aquahub.t5lamp.appsettings.json', 'r') as config_file:
    config = json.load(config_file)

# Setup logging
log_file_name = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'logs/ds18b20_sensor.log')
logging.basicConfig(handlers=[TimedRotatingFileHandler(log_file_name, when="midnight", interval=1, backupCount=7)],
                    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize MQTT Client
client = mqtt.Client("DS18B20_Publisher")
mqtt_user = config.get('MQTT_USER', '')
mqtt_password = config.get('MQTT_PASSWORD', '')
if mqtt_user and mqtt_password:
    client.username_pw_set(mqtt_user, mqtt_password)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish

# Connect to MQTT Broker
client.connect(config['MQTT_SERVER'])
client.loop_start()

# Initialize sensor
sensor = W1ThermSensor()

while True:
    try:
        logging.info("Starting loop cycle")                
        temperature = round(sensor.get_temperature(), 2)
        logging.info(f"Measured temperature: {temperature}")        
        client.publish(config['DS18B20_TOPIC'], temperature)
        logging.info(f"Published temperature: {temperature} to MQTT topic {config['DS18B20_TOPIC']}")
    except Exception as e:
        logging.error(f"Error reading from DS18B20 or publishing to MQTT: {e}")

    # Sleep for the configured update interval
    update_interval = config.get('T5LAMP_UPDATE_INTERVAL', 5)  # Default to 5 seconds if not set
    time.sleep(update_interval)