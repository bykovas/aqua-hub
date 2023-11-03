import threading
import sys
import time

from schedule import Schedule
from DRF0971driver import *
import webserver

def main() -> int:
    t = threading.Thread(target=webserver.start_api_server)
    t.daemon = True
    t.start()

    while True:
        current_values = Schedule.get_current_values()
        if Schedule.is_demo_mode():
            print('Running in demo mode')
        else:
            dac.set_dac_out_voltage(current_values[0], CHANNEL_0)
            dac.set_dac_out_voltage(current_values[1], CHANNEL_1)
            print(f'Ch0: {current_values[0]}, Ch1: {current_values[1]}, demo: {Schedule.is_demo_mode()}')

        time.sleep(1)

if __name__ == '__main__':
    dac = DRF0971Driver()
    sys.exit(main())
