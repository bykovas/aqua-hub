import smbus

# Constants for selecting voltage range and channels
OUTPUT_RANGE_5V = 0
OUTPUT_RANGE_10V = 17
CHANNEL_0 = 1
CHANNEL_1 = 2
CHANNEL_ALL = 3
CONFIG_CURRENT_REG = 0x02
ADDRESS = 0x5F  # Address should be in uppercase for constants
MAX_VOLTAGE = 5000  # Add a constant for default voltage


class DRF0971Driver:
    def __init__(self):
        self._addr = ADDRESS
        self._out_put_set_range = 0x01  # Use snake_case for variable names
        self._scl = 3
        self._sda = 2
        self._data_transmission = 0
        self._i2c = smbus.SMBus(1)
        self._set_dac_out_range(OUTPUT_RANGE_10V)
        self.set_dac_out_voltage(MAX_VOLTAGE, CHANNEL_ALL)

    def set_dac_out_voltage(self, percentage, channel):
        voltage = percentage * MAX_VOLTAGE / 100;
        data_transmission = int((voltage / MAX_VOLTAGE) * 4095) << 4
        self._send_data(data_transmission, channel)

    def begin(self):
        read_byte = self._i2c.read_byte(self._addr)
        return read_byte == 0

    def _set_dac_out_range(self, output_range):
        self._i2c.write_word_data(self._addr, self._out_put_set_range, output_range)

    def _send_data(self, data, channel):
        if channel == CHANNEL_0:
            self._i2c.write_word_data(self._addr, CONFIG_CURRENT_REG, data)
        elif channel == CHANNEL_1:
            self._i2c.write_word_data(self._addr, CONFIG_CURRENT_REG << 1, data)
        else:  # Assuming CHANNEL_ALL
            self._i2c.write_word_data(self._addr, CONFIG_CURRENT_REG, data)
            self._i2c.write_word_data(self._addr, CONFIG_CURRENT_REG << 1, data)