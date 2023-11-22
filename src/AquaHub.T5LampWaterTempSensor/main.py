import time
from w1thermsensor import W1ThermSensor
import paho.mqtt.client as mqtt

broker_address = "192.168.1.11"
topic = "ahub/light/water_temp/out"

client = mqtt.Client("DS18B20_Publisher")
client.connect(broker_address)

sensor = W1ThermSensor()

while True:
    temperature = sensor.get_temperature()

    client.publish(topic, temperature)

    time.sleep(5)