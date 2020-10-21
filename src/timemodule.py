from machine import Pin, I2C
from ds3231 import DS3231

time_module = DS3231(I2C(sda=Pin(21), scl=Pin(22)))


def now():
    return time_module.DateTime()
