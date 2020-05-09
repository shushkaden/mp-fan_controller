from machine import Pin, ADC


class Tempsensor:
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

