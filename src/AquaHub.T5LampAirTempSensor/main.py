import Adafruit_DHT
import paho.mqtt.client as mqtt
import time
import json
import logging
from logging.handlers import TimedRotatingFileHandler
import os

# Load configuration from a JSON file
with open('/apps/aquahub.t5lamp.appsettings.json', 'r') as config_file:
    config = json.load(config_file)

# Setup logging
log_file_name = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'dht_sensor.log')
logging.basicConfig(handlers=[TimedRotatingFileHandler(log_file_name, when="midnight", interval=1, backupCount=7)],
                    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# DHT22 sensor setup
sensor = Adafruit_DHT.DHT22
gpio_pin = config['DHT_GPIO_PIN']

# MQTT client setup
client = mqtt.Client()
client.connect(config['MQTT_SERVER'])
client.loop_start()

try:
    while True:
        temp_sum = 0.0
        hum_sum = 0.0
        valid_readings = 0

        for _ in range(10):
            humidity, temperature = Adafruit_DHT.read_retry(sensor, gpio_pin)
            if humidity is not None and temperature is not None:
                temp_sum += temperature
                hum_sum += humidity
                valid_readings += 1
            time.sleep(0.5)

        if valid_readings > 0:
            avg_temperature = round(temp_sum / valid_readings, 2)
            avg_humidity = round(hum_sum / valid_readings, 2)

            client.publish(config['MQTT_TEMP_TOPIC'], str(avg_temperature))
            client.publish(config['MQTT_HUMIDITY_TOPIC'], str(avg_humidity))
        else:
            logging.error("Failed to retrieve data from the sensor")
        
        update_interval = config.get('T5LAMP_UPDATE_INTERVAL', 5) # Default to 5 seconds if not set
        time.sleep(update_interval)

except KeyboardInterrupt:
    logging.info("Sensor reading stopped by user")

finally:
    client.loop_stop()
    client.disconnect()
    logging.info("MQTT client disconnected")