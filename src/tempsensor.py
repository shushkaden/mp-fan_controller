from machine import Pin, ADC


class ADCReader:
    values = []
    sensor = None

    def __init__(self, pin=32):
        self.sensor = ADC(Pin(pin))
        self.sensor.atten(ADC.ATTN_11DB)

    def read(self):
        value = self.sensor.read()
        self.values.append(value)
        while len(self.values) > 10:
            self.values.pop(0)

        return value

    def get_value(self):
        if not self.values:
            return self.read()

        max_value = max(self.values)
        min_value = min(self.values)
        max_values = []
        min_values = []

        for value in self.values:
            if (max_value - value) < (value - min_value):
                max_values.append(value)
            else:
                min_values.append(value)

        good_values = max_values if len(max_values) > len(min_values) else min_values
        value = sum(good_values)/len(good_values)

        return int(value)


class SmoothValue:
    value = None
    min_value = None
    max_value = None
    divider = None

    def __init__(self, min_value, max_value, divider):
        self.min_value = min_value
        self.max_value = max_value
        self.divider = divider

    def get_smooth(self, value):
        if not self.value:
            self.value = value
            return value

        diff = value - self.value

        smoother = abs(diff)
        smoother /= self.divider
        smoother = max(smoother, self.min_value)
        smoother = min(smoother, self.max_value)

        diff *= smoother

        self.value = self.value + diff

        return self.value


class Tempsensor:
    adc_reader = None
    values = []
    range = 6
    smooth_temp = SmoothValue(0.05, 1, 2)
    smooth_temp_result = SmoothValue(0.05, 1, 2)
    smooth_delta = SmoothValue(0.1, 1, 1)
    # parameters for formula
    # y = ax ^ 3 + bx ^ 2 + cx + d
    # where x is adc value and y is temperature
    # several ranges for a higher precision
    # VALUES WORKS ONLY FOR 266 OHMS RESISTOR IN VOLTAGE DEVIDER!
    # AND TEMPERATURE SENSOR FAE 33060
    adc_temperature_dependancy = [
        {'value': 748, 'a': 0.000000004, 'b': -0.0000172055, 'c': 0.05823517, 'd': 21.4181976964},
        {'value': 0, 'a': 0.0000000706, 'b': -0.0001253021, 'c': 0.1171149112, 'd': 9.9836620549},
    ]

    def __init__(self, pin=32):
        self.adc_reader = ADCReader(pin=pin)

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
        adc_value = self.adc_reader.get_value()
        temperature = self._calculate_temperature(adc_value)

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
        raw_temperature = self.smooth_temp.get_smooth(self._read_temperature())
        if len(self.values) < self.range:
            self._save(raw_temperature)

            return {
                'raw_temperature': raw_temperature,
                'temperature': raw_temperature,
                'raw_delta': 0,
                'delta': 0,
            }

        raw_delta = raw_temperature - self.values[0]
        delta = self.smooth_delta.get_smooth(raw_delta)
        self._save(raw_temperature)
        temperature = self.smooth_temp_result.get_smooth(raw_temperature + self._get_increment_by_delta(delta))

        return {
            'raw_temperature': raw_temperature,
            'temperature': temperature,
            'raw_delta': raw_delta,
            'delta': delta,
        }
