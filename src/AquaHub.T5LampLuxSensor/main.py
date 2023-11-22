import smbus
import time
import paho.mqtt.client as mqtt

# Setup for BH1750
bus = smbus.SMBus(1)  # Using I2C bus 1
BH1750_ADDRESS = 0x23
BH1750_POWER_DOWN = 0x00
BH1750_POWER_ON = 0x01
BH1750_RESET = 0x07
BH1750_CONTINUOUS_HIGH_RES_MODE = 0x10

# MQTT client setup
client = mqtt.Client()
client.connect("192.168.1.11")  # Address of the MQTT broker
client.loop_start()

def read_light():
    # Read data from BH1750
    data = bus.read_i2c_block_data(BH1750_ADDRESS, BH1750_CONTINUOUS_HIGH_RES_MODE, 2)
    return (data[1] + (256 * data[0])) / 1.2

try:
    while True:
        light_level = read_light()
        # Publish light level data
        client.publish("ahub/light/lux/out", str(light_level))
        time.sleep(5)
except KeyboardInterrupt:
    pass

# Clean up on exit
client.loop_stop()
client.disconnect()