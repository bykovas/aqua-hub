import sys
import time
import paho.mqtt.client as mqtt
import logging
from DRF0971driver import *

# Configure logging with an identifier for the specific application
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - AquaHub.T5LampController - %(levelname)s - %(message)s')

# Function to log messages
def log_message(message):
    full_message = f"AquaHub.T5LampController - {message}"
    try:
        client.publish("ahub/logs/error", full_message)
    except Exception:
        logging.error(full_message)

# Callback function for processing received MQTT messages
def on_message(client, userdata, message):
    try:
        value = int(message.payload.decode())
        if message.topic == "ahub/light/t5blue/in":
            dac.set_dac_out_voltage(value, CHANNEL_0)
            userdata['t5blue'] = value
        elif message.topic == "ahub/light/t5coral/in":
            dac.set_dac_out_voltage(value, CHANNEL_1)
            userdata['t5coral'] = value
    except ValueError:
        log_message(f"Error: Invalid value received in topic {message.topic}")

# Main function
def main() -> int:
    client_userdata = {'t5blue': 0, 't5coral': 0}
    client = mqtt.Client(userdata=client_userdata)
    client.on_message = on_message

    try:
        client.connect("192.168.1.11")
    except Exception as e:
        log_message(f"An error occurred: {e}")
        sys.exit(1)

    client.subscribe("ahub/light/t5blue/in")
    client.subscribe("ahub/light/t5coral/in")
    client.loop_start()

    dac.set_dac_out_voltage(0, CHANNEL_0)
    dac.set_dac_out_voltage(0, CHANNEL_1)

    try:
        while True:
            client.publish("ahub/light/t5blue/out", str(client_userdata['t5blue']))
            client.publish("ahub/light/t5coral/out", str(client_userdata['t5coral']))
            time.sleep(5)
    except KeyboardInterrupt:
        pass
    finally:
        client.loop_stop()
        client.disconnect()

# Entry point
if __name__ == '__main__':
    try:
        dac = DRF0971Driver()
        sys.exit(main())
    except Exception as e:
        log_message(f"An error occurred: {e}")