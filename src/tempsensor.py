from machine import Pin, ADC

from smooth import SmoothValue


class ADCReader:

    def __init__(self, pin=32):
        self.values = []
        self.sensor = ADC(Pin(pin))
        self.sensor.atten(ADC.ATTN_11DB)
        self.values_range = 40
        self.edge = round(self.values_range * 0.2)

    def read(self):
        value = self.sensor.read()
        self.values.append(value)
        while len(self.values) > self.values_range:
            self.values.pop(0)

        return value

    def get_value(self):
        if len(self.values) < self.values_range:
            return self.read()

        values = sorted(self.values.copy())
        values = values[self.edge:len(values)-self.edge]
        value = sum(values) / len(values)

        return int(value)


class Tempsensor:

    def __init__(self, pin):
        self.adc_reader = ADCReader(pin=pin)

        self.values = []
        self.range = 6  # seconds +1
        self.smooth_raw_temperature = SmoothValue(0.05, 1, 2)
        self.smooth_temperature = SmoothValue(0.05, 1, 2)
        self.smooth_delta = SmoothValue(0.1, 1, 1)
        # parameters for formula
        # y = ax ^ 3 + bx ^ 2 + cx + d
        # where x is adc value and y is temperature
        # several ranges for a higher precision
        # VALUES WORKS ONLY FOR 266 OHMS RESISTOR IN VOLTAGE DEVIDER!
        # AND TEMPERATURE SENSOR FAE 33060
        self.adc_temperature_dependancy = [
            {'value': 765, 'a': 0.0000000041, 'b': -0.0000169431, 'c': 0.05483747, 'd': 23.3167608512},
            {'value': 0, 'a': 0.0000000682, 'b': -0.0001242755, 'c': 0.1168440757, 'd': 9.9987971976},
        ]

        self.current_adc_temperature = 0
        self.current_raw_temperature = 0
        self.current_temperature = 0
        self.current_raw_delta = 0
        self.current_delta = 0
        self.adc_value = 0

    def tick(self):
        self.adc_reader.read()

    def _calculate_temperature(self, adc_value):
        parameters = next(params for params in self.adc_temperature_dependancy if adc_value >= params['value'])
        temperature = parameters['a'] * adc_value**3 + \
                      parameters['b'] * adc_value**2 + \
                      parameters['c'] * adc_value + \
                      parameters['d']

        return temperature

    def _read_temperature(self):
        self.adc_value = self.adc_reader.get_value()
        temperature = self._calculate_temperature(self.adc_value)

        return temperature

    def _save(self, value):
        self.values.append(value)
        while len(self.values) > self.range:
            self.values.pop(0)

    def _get_increment_by_delta(self, delta):
        if delta == 0:
            return 0

        sign = delta/abs(delta)
        return sign * pow(abs(delta), 0.7) * 3.1

    def get_temperature(self):
        self.current_adc_temperature = self._read_temperature()
        raw_temperature = self.smooth_raw_temperature.get_smooth(self.current_adc_temperature)
        if len(self.values) < self.range:
            self._save(raw_temperature)

            self.current_raw_temperature = raw_temperature
            self.current_temperature = raw_temperature

            return self.current_temperature

        raw_delta = raw_temperature - self.values[0]
        delta = self.smooth_delta.get_smooth(raw_delta)
        self._save(raw_temperature)
        temperature = self.smooth_temperature.get_smooth(raw_temperature + self._get_increment_by_delta(delta))

        self.current_raw_temperature = raw_temperature
        self.current_temperature = temperature
        self.current_raw_delta = raw_delta
        self.current_delta = delta

        return self.current_temperature
