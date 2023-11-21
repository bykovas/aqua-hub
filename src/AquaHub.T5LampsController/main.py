import sys
import time
import paho.mqtt.client as mqtt

from DRF0971driver import *

# Callback function for processing received messages
def on_message(client, userdata, message):
    value = int(message.payload.decode())
    # Set DAC voltage for t5blue channel
    if message.topic == "ahub/light/t5blue/in":
        dac.set_dac_out_voltage(value, CHANNEL_0)
        userdata['t5blue'] = value
    # Set DAC voltage for t5coral channel
    elif message.topic == "ahub/light/t5coral/in":
        dac.set_dac_out_voltage(value, CHANNEL_1)
        userdata['t5coral'] = value

def main() -> int:
    # Initialize MQTT client
    client_userdata = {'t5blue': 0, 't5coral': 0}
    client = mqtt.Client(userdata=client_userdata)
    client.on_message = on_message

    # Connect to MQTT server
    client.connect("192.168.1.11")

    # Subscribe to topics
    client.subscribe("ahub/light/t5blue/in")
    client.subscribe("ahub/light/t5coral/in")

    # Start MQTT loop
    client.loop_start()

    # Initialize DAC with 0 voltage
    dac.set_dac_out_voltage(0, CHANNEL_0)
    dac.set_dac_out_voltage(0, CHANNEL_1)

    while True:
        # Publish current values to MQTT topics
        client.publish("ahub/light/t5blue/out", str(client_userdata['t5blue']))
        client.publish("ahub/light/t5coral/out", str(client_userdata['t5coral']))

        time.sleep(5)

if __name__ == '__main__':
    dac = DRF0971Driver()
    sys.exit(main())