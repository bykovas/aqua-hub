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

# Setting up logging
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
        self.last_command_time = time.time()

    def log_message(self, message):
        """Logs a message to the file."""
        logging.error(f"AquaHub.T5LampController - {message}")

    def on_message(self, client, userdata, message):
        """Processes incoming MQTT messages."""
        try:
            value = int(message.payload.decode())
            if message.topic in [config['T5BLUE_TOPIC_IN'], config['T5CORAL_TOPIC_IN']]:
                if time.time() - self.last_command_time > 60:
                    self.handle_regular_command(message.topic, value, userdata)
            elif message.topic in [config['T5BLUE_HA_TOPIC'], config['T5CORAL_HA_TOPIC']]:
                self.handle_ha_command(message.topic, value, userdata)
                self.last_command_time = time.time()
        except ValueError:
            self.log_message(f"Error: Invalid value received in topic {message.topic}")

    def handle_regular_command(self, topic, value, userdata):
        """Handles regular commands."""
        if topic == config['T5BLUE_TOPIC_IN']:
            self.dac.set_dac_out_voltage(value, CHANNEL_0)
            userdata['t5blue'] = value
            self.publish_status('t5blue', value)
        elif topic == config['T5CORAL_TOPIC_IN']:
            self.dac.set_dac_out_voltage(value, CHANNEL_1)
            userdata['t5coral'] = value
            self.publish_status('t5coral', value)

    def handle_ha_command(self, topic, payload, userdata):
        """Handles commands from Home Assistant."""
        try:
            payload_dict = json.loads(payload)
            state = payload_dict.get("state")
            brightness = payload_dict.get("brightness")

            if state == "ON":
                if brightness is not None:
                    dac_value = brightness #int((brightness / 100.0) * 4095)
                else:
                    dac_value = userdata.get(f'{topic}_last_brightness', 50)
            elif state == "OFF":
                dac_value = 0
            else:
                return

            if topic == config['T5BLUE_HA_TOPIC']:
                self.dac.set_dac_out_voltage(dac_value, CHANNEL_0)
                userdata['t5blue'] = dac_value
                self.publish_status('t5blue', dac_value)
            elif topic == config['T5CORAL_HA_TOPIC']:
                self.dac.set_dac_out_voltage(dac_value, CHANNEL_1)
                userdata['t5coral'] = dac_value
                self.publish_status('t5coral', dac_value)

            if brightness is not None:
                userdata[f'{topic}_last_brightness'] = dac_value
        except json.JSONDecodeError:
            self.log_message(f"Error: Invalid JSON received in topic {topic}")


    def run(self):
        """Main loop of the controller."""
        try:
            mqtt_user = config.get('MQTT_USER', '')
            mqtt_password = config.get('MQTT_PASSWORD', '')
            if mqtt_user and mqtt_password:
                self.client.username_pw_set(mqtt_user, mqtt_password)            
            self.client.connect(config['MQTT_SERVER'])
            self.client.subscribe(config['T5BLUE_TOPIC_IN'])
            self.client.subscribe(config['T5CORAL_TOPIC_IN'])
            self.client.loop_start()

            # MQTT Discovery for Home Assistant
            self.register_with_home_assistant()

            while True:
                time.sleep(10) # Interval for any periodic tasks
        except KeyboardInterrupt:
            pass
        except Exception as e:
            self.log_message(f"An error occurred: {e}")
        finally:
            self.client.loop_stop()
            self.client.disconnect()

    def register_with_home_assistant(self):
        """Registers devices with Home Assistant using MQTT Discovery."""
        base_topic = config.get('MQTT_DISCOVERY_PREFIX', 'homeassistant')
        unique_id_blue = 't5blue_lamp'
        unique_id_coral = 't5coral_lamp'

        # T5 Blue Lamp
        config_topic_blue = f"{base_topic}/light/{unique_id_blue}/config"
        self.client.publish(config_topic_blue, json.dumps({
            "name": "T5 Blue Lamp",
            "unique_id": unique_id_blue,
            "stat_t": f"{config['T5BLUE_TOPIC_OUT']}",
            "cmd_t": f"{config['T5BLUE_HA_TOPIC']}",
            "bri_stat_t": f"{config['T5BLUE_TOPIC_OUT']}",
            "bri_cmd_t": f"{config['T5BLUE_HA_TOPIC']}",
            "bri_scl": 100,
            "brightness": True,
            "on_cmd_type": "brightness",
            "schema": "json"
        }), retain=True)

        # T5 Coral Lamp
        config_topic_coral = f"{base_topic}/light/{unique_id_coral}/config"
        self.client.publish(config_topic_coral, json.dumps({
            "name": "T5 Coral Lamp",
            "unique_id": unique_id_coral,
            "stat_t": f"{config['T5CORAL_TOPIC_OUT']}",
            "cmd_t": f"{config['T5CORAL_HA_TOPIC']}",
            "bri_stat_t": f"{config['T5CORAL_TOPIC_OUT']}",
            "bri_cmd_t": f"{config['T5CORAL_HA_TOPIC']}",
            "bri_scl": 100,
            "brightness": True,
            "on_cmd_type": "brightness",
            "schema": "json"
        }), retain=True)


    def publish_status(self, lamp, brightness):
        """Publishes the current status to the MQTT server."""
        state_topic = config[f'{lamp.upper()}_TOPIC_OUT']
        self.client.publish(state_topic, json.dumps({"state": "ON", "brightness": brightness}), retain=True)

# Entry point of the program
if __name__ == '__main__':
    try:
        controller = T5LampController()
        sys.exit(controller.run())
    except Exception as e:
        logging.error(f"AquaHub.T5LampController - An error occurred: {e}")
