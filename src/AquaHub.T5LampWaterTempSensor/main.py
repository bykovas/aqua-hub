import time
import json
import logging
from logging.handlers import TimedRotatingFileHandler
import os
from w1thermsensor import W1ThermSensor
import paho.mqtt.client as mqtt

# Load configuration from a JSON file
with open('/apps/aquahub.t5lamp.appsettings.json', 'r') as config_file:
    config = json.load(config_file)

# Setup logging
log_file_name = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'ds18b20_sensor.log')
logging.basicConfig(handlers=[TimedRotatingFileHandler(log_file_name, when="midnight", interval=1, backupCount=7)],
                    level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

client = mqtt.Client("DS18B20_Publisher")
client.connect(config['MQTT_SERVER'])

sensor = W1ThermSensor()

while True:
    try:
        temperature = round(sensor.get_temperature(), 2)
        client.publish(config['DS18B20_TOPIC'], temperature)
    except Exception as e:
        logging.error(f"Error reading from DS18B20: {e}")

    update_interval = config.get('T5LAMP_UPDATE_INTERVAL', 5) # Default to 5 seconds if not set
    time.sleep(update_interval)
