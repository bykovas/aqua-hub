import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
pwm = GPIO.PWM(17, 1000)  # Create PWM on pin 17 at 1000 Hz
pwm.start(0)

current_power = 0  # Variable to store the current power level

# Callback function to handle incoming messages
def on_message(client, userdata, message):
    global current_power
    current_power = float(message.payload.decode())
    pwm.ChangeDutyCycle(current_power)  # Change duty cycle based on received message

# MQTT client setup
client = mqtt.Client()
client.on_message = on_message

client.connect("192.168.1.11")  # Connect to MQTT broker
client.subscribe("ahub/light/fan/in")  # Subscribe to topic
client.loop_start()

try:
    while True:
        # Publish current power every 5 seconds
        client.publish("ahub/light/fan/out", str(current_power))
        time.sleep(5)
except KeyboardInterrupt:
    pass

pwm.stop()
GPIO.cleanup()
