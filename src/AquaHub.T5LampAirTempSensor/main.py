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
        temp_sum = 0.0
        hum_sum = 0.0
        valid_readings = 0

        for _ in range(10):  # Measure 10 times
            humidity, temperature = Adafruit_DHT.read_retry(sensor, gpio_pin)
            if humidity is not None and temperature is not None:
                temp_sum += temperature
                hum_sum += humidity
                valid_readings += 1
            time.sleep(0.5)  # Delay between individual readings

        if valid_readings > 0:
            # Calculate average temperature and humidity
            avg_temperature = round(temp_sum / valid_readings, 1)
            avg_humidity = round(hum_sum / valid_readings, 1)

            # Publish average temperature and humidity data
            client.publish("ahub/light/air_temp/out", str(avg_temperature))
            client.publish("ahub/light/air_humidity/out", str(avg_humidity))
        else:
            print("Failed to retrieve data from the sensor")

        time.sleep(5)  # Delay between sets of readings

except KeyboardInterrupt:
    pass

# Clean up on exit
client.loop_stop()
client.disconnect()
