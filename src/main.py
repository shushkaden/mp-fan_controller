import uos
from machine import SDCard, Pin, I2C, Timer

from ds3231 import DS3231
from tempsensor import Tempsensor
from utils import leading_zero

time_module = DS3231(I2C(sda=Pin(21), scl=Pin(22)))
now = time_module.DateTime()
tempsensor = Tempsensor(pin=32)

uos.mount(SDCard(slot=2, sck=18, miso=19, mosi=23, cs=5), "/sd")

if 'sensor_log' not in uos.listdir('/sd'):
    uos.mkdir('/sd/sensor_log')

filename = '/sd/sensor_log/log_{year}-{month}-{day}_{hour}-{minute}-{second}.csv'.format(
    year=now[0],
    month=leading_zero(now[1]),
    day=leading_zero(now[2]),
    hour=leading_zero(now[4]),
    minute=leading_zero(now[5]),
    second=leading_zero(now[6]))

with open(filename, 'w') as file:
    file.write('time, voltage\n')

main_timer = Timer(-1)

counter = 0

def tick(timer):
    global counter
    counter += 1

    if counter == 100:
        log_sensors_data()
        counter = 0

    tempsensor.read()


def log_sensors_data():
    voltage = tempsensor.get_value()
    now = time_module.DateTime()
    nowstr = '{hour}:{minute}:{second}'.format(
        hour=leading_zero(now[4]),
        minute=leading_zero(now[5]),
        second=leading_zero(now[6]))

    # print('{time}, {voltage}'.format(time=nowstr, voltage=voltage))

    with open(filename, 'a') as file:
        file.write('{time}, {voltage}\n'.format(time=nowstr, voltage=voltage))

def main():
    main_timer.init(period=50, mode=Timer.PERIODIC, callback=tick)

if __name__ == '__main__':
    main()
