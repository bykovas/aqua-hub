import RPi.GPIO as GPIO
import time

# Initialize GPIO
PIN_BUZZER_OUT = 4
PIN_BUTTON_IN = 22
PIN_LED = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_BUZZER_OUT, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(PIN_BUTTON_IN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_LED, GPIO.OUT, initial=GPIO.LOW)

# Time parameters
max_on_time = 10
min_on_time = 3
max_off_time = 60

# Timekeeping variables
last_button_press_time = time.time()
led_on_time = 0
is_led_on = False

def beep(buzzer_pin, duration):
    GPIO.output(buzzer_pin, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(buzzer_pin, GPIO.LOW)

try:
    beep(PIN_BUZZER_OUT, 0.5)       
    while True:
        button_state = GPIO.input(PIN_BUTTON_IN)
        button_pressed = button_state == 0
        current_time = time.time()
        
        print(f"Button State: {button_state}, LED On: {is_led_on}")

        if current_time - last_button_press_time > max_off_time:
            print("Warning! The button has not been pressed for 1 minute.")
            print("Activating beep due to max_off_time.")            
            beep(PIN_BUZZER_OUT, 0.5)  # Beep for 0.5 seconds

        if button_pressed:
            last_button_press_time = current_time
            
            if not is_led_on:
                GPIO.output(PIN_LED, 1)
                led_on_time = current_time
                is_led_on = True
            elif current_time - led_on_time >= max_on_time:
                print("Turning off the LED due to max_on_time.")
                GPIO.output(PIN_LED, 0)
                is_led_on = False
                print("Activating beep due to max_on_time.")                
                beep(PIN_BUZZER_OUT, 0.5)  # Beep for 0.5 seconds

        else:
            if is_led_on and current_time - led_on_time >= min_on_time:
                GPIO.output(PIN_LED, 0)
                is_led_on = False

        time.sleep(0.5)

finally:
    print("Cleaning up GPIO settings.")
    GPIO.cleanup()
