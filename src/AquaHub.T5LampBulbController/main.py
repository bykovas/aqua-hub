import sys
import time
import json
import paho.mqtt.client as mqtt
import logging
from logging.handlers import TimedRotatingFileHandler
from DRF0971driver import DRF0971Driver, CHANNEL_0, CHANNEL_1
import os

# Load configuration from a JSON file
with open('/apps/aquahub.t5lamp.appsettings.json', 'r') as config_file:
    config = json.load(config_file)

# Setting up logging to a file with rotation every day
log_directory = '/apps/AquaHub.T5LampBulbController/logs'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
log_file_path = '/apps/AquaHub.T5LampBulbController/logs/t5lamp.log'
logging.basicConfig(handlers=[TimedRotatingFileHandler(log_file_path, when="midnight", interval=1, backupCount=5)],
                    level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

class T5LampController:
    def __init__(self):
        self.dac = DRF0971Driver()
        self.client = mqtt.Client(userdata={'t5blue': 0, 't5coral': 0})
        self.client.on_message = self.on_message

    def log_message(self, message):
        """ Logs a message to the file """
        logging.error(f"AquaHub.T5LampController - {message}")

    def on_message(self, client, userdata, message):
        """ Processes incoming MQTT messages """
        try:
            value = int(message.payload.decode())
            if message.topic == config['T5BLUE_TOPIC_IN']:
                self.dac.set_dac_out_voltage(value, CHANNEL_0)
                userdata['t5blue'] = value
            elif message.topic == config['T5CORAL_TOPIC_IN']:
                self.dac.set_dac_out_voltage(value, CHANNEL_1)
                userdata['t5coral'] = value
        except ValueError:
            self.log_message(f"Error: Invalid value received in topic {message.topic}")

    def run(self):
        """ Main loop of the controller """
        try:
            self.client.connect(config['MQTT_SERVER'])
            self.client.subscribe(config['T5BLUE_TOPIC_IN'])
            self.client.subscribe(config['T5CORAL_TOPIC_IN'])
            self.client.loop_start()

            self.dac.set_dac_out_voltage(0, CHANNEL_0)
            self.dac.set_dac_out_voltage(0, CHANNEL_1)

            update_interval = config.get('T5LAMP_UPDATE_INTERVAL', 5) # Default to 5 seconds if not set
            while True:
                self.publish_status()
                time.sleep(update_interval)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            self.log_message(f"An error occurred: {e}")
        finally:
            self.client.loop_stop()
            self.client.disconnect()

    def publish_status(self):
        """ Publishes the current status to the MQTT server """
        userdata = self.client._userdata
        self.client.publish(config['T5BLUE_TOPIC_OUT'], str(userdata['t5blue']))
        self.client.publish(config['T5CORAL_TOPIC_OUT'], str(userdata['t5coral']))

# Entry point of the program
if __name__ == '__main__':
    try:
        controller = T5LampController()
        sys.exit(controller.run())
    except Exception as e:
        logging.error(f"AquaHub.T5LampController - An error occurred: {e}")