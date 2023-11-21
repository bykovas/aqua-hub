import Adafruit_DHT
import paho.mqtt.client as mqtt
import time

# DHT22 sensor setup
sensor = Adafruit_DHT.DHT22
gpio_pin = 4  # GPIO pin to which DHT22 is connected

# MQTT client setup
client = mqtt.Client()
client.connect("192.168.1.11")  # Address of the MQTT broker
client.loop_start()

try:
    while True:
        # Read data from the DHT22 sensor
        humidity, temperature = Adafruit_DHT.read_retry(sensor, gpio_pin)
        if humidity is not None and temperature is not None:
            # Publish temperature and humidity data
            client.publish("ahub/light/air_temp/out", str(temperature))
            client.publish("ahub/light/air_humidity/out", str(humidity))
        else:
            print("Failed to retrieve data from the sensor")

        time.sleep(5)  # Delay between readings

except KeyboardInterrupt:
    pass

# Clean up on exit
client.loop_stop()
client.disconnect()