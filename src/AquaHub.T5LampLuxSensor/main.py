import smbus
import time
import paho.mqtt.client as mqtt
import json
import logging
from logging.handlers import TimedRotatingFileHandler
import os

# Load configuration from a JSON file
with open('/apps/aquahub.t5lamp.appsettings.json', 'r') as config_file:
    config = json.load(config_file)

# Setup logging
log_file_name = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'bh1750_sensor.log')
logging.basicConfig(handlers=[TimedRotatingFileHandler(log_file_name, when="midnight", interval=1, backupCount=7)],
                    level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Setup for BH1750
bus = smbus.SMBus(1)  # Using I2C bus 1
BH1750_ADDRESS = 0x23
BH1750_POWER_DOWN = 0x00
BH1750_POWER_ON = 0x01
BH1750_RESET = 0x07
BH1750_CONTINUOUS_HIGH_RES_MODE = 0x10

# MQTT client setup
client = mqtt.Client()
client.connect(config['MQTT_SERVER'])  # Address of the MQTT broker
client.loop_start()

def read_light():
    try:
        data = bus.read_i2c_block_data(BH1750_ADDRESS, BH1750_CONTINUOUS_HIGH_RES_MODE, 2)
        return round((data[1] + (256 * data[0])) / 1.2, 2)
    except Exception as e:
        logging.error(f"Error reading from BH1750: {e}")
        return None

try:
    while True:
        light_level = read_light()
        if light_level is not None:
            client.publish(config['MQTT_LUX_TOPIC'], str(light_level))
        update_interval = config.get('T5LAMP_UPDATE_INTERVAL', 5) # Default to 5 seconds if not set
        time.sleep(update_interval)
        
except KeyboardInterrupt:
    logging.info("Sensor reading stopped by user")
finally:
    client.loop_stop()
    client.disconnect()
    logging.info("MQTT client disconnected")
