from machine import Pin
from max6675 import MAX6675

class Thermocouple:
    values = []

    def __init__(self, sck=None, cs=None, so=None):
        sck = sck or Pin(18, Pin.OUT)
        cs = cs or Pin(4, Pin.OUT)
        so = so or Pin(19, Pin.IN)
        self.sensor = MAX6675(sck=sck, cs=cs, so=so)

    def read(self):
        value = self.sensor.read()
        self.values.append(value)
        while len(self.values) > 10:
            self.values.pop(0)

        return value

    def get_value(self):
        if not self.values:
            return self.read()

        value = sum(self.values)/len(self.values)

        return float("{0:.2f}".format(value))
