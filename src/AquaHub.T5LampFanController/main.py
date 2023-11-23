import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time
import json
import logging
from logging.handlers import TimedRotatingFileHandler
import os

# Load configuration from a JSON file
with open('/apps/aquahub.t5lamp.appsettings.json', 'r') as config_file:
    config = json.load(config_file)

# Setup logging
log_file_name = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fan_control.log')
logging.basicConfig(handlers=[TimedRotatingFileHandler(log_file_name, when="midnight", interval=1, backupCount=7)],
                    level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
pwm = GPIO.PWM(17, 1000)  # Create PWM on pin 17 at 1000 Hz
pwm.start(0)

current_power = 0  # Variable to store the current power level

# Callback function to handle incoming messages
def on_message(client, userdata, message):
    global current_power
    try:
        current_power = float(message.payload.decode())
        pwm.ChangeDutyCycle(current_power)  # Change duty cycle based on received message
    except Exception as e:
        logging.error(f"Error handling message: {e}")

# MQTT client setup
client = mqtt.Client()
client.on_message = on_message

client.connect(config['MQTT_SERVER'])  # Connect to MQTT broker
client.subscribe(config['FAN_IN_TOPIC'])  # Subscribe to topic
client.loop_start()

try:
    while True:
        # Publish current power every 5 seconds
        client.publish(config['FAN_OUT_TOPIC'], str(current_power))
        update_interval = config.get('T5LAMP_UPDATE_INTERVAL', 5) # Default to 5 seconds if not set
        time.sleep(update_interval)
        
except KeyboardInterrupt:
    logging.info("Fan control stopped by user")
finally:
    pwm.stop()
    GPIO.cleanup()
    client.loop_stop()
    client.disconnect()
    logging.info("MQTT client disconnected")