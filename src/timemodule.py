from machine import Pin, I2C
from ds3231 import DS3231

time_module = DS3231(I2C(sda=Pin(21), scl=Pin(22)))


def now():
    return time_module.DateTime()


def set_datetime(year, month, day, hour, minute, second):
    time_module.Year(year)
    time_module.Month(month)
    time_module.Day(day)
    time_module.Hour(hour)
    time_module.Minute(minute)
    time_module.Second(second)
