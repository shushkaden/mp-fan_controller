import uos
from machine import SDCard, Pin, I2C, Timer

from ds3231 import DS3231
from pwmfan import PWMFan
from pid import PIDFanTempController
from tempsensor import Tempsensor
from thermocouple import Thermocouple
from utils import leading_zero

time_module = DS3231(I2C(sda=Pin(21), scl=Pin(22)))
now = time_module.DateTime()
tempsensor = Tempsensor(pin=32)
thermocouple = Thermocouple()
fan = PWMFan()
fan_controller = PIDFanTempController(fan, tempsensor)

# uos.mount(SDCard(slot=2, sck=18, miso=19, mosi=23, cs=5), "/sd")
#
# if 'sensor_log' not in uos.listdir('/sd'):
#     uos.mkdir('/sd/sensor_log')

if 'sensor_log' not in uos.listdir(''):
    uos.mkdir('/sensor_log')

filename = '/sensor_log/log_{year}-{month}-{day}_{hour}-{minute}-{second}.csv'.format(
    year=now[0],
    month=leading_zero(now[1]),
    day=leading_zero(now[2]),
    hour=leading_zero(now[4]),
    minute=leading_zero(now[5]),
    second=leading_zero(now[6]))

with open(filename, 'w') as file:
    file.write('time; thermocouple_temp; raw_temp; temp; raw_delta; delta\n')

main_timer = Timer(-1)
counter = 0


def tick(timer):
    global counter
    counter += 1

    if counter == 20:
        log_sensors_data()
        fan_controller.update_fan_speed()
        counter = 0

    tempsensor.tick()
    thermocouple.read()
    fan.tick(50)


def to_log_value(val):
    return str(val).replace('.', ',')


def log_sensors_data():
    tempsensor.get_temperature()
    thermocouple_temp = thermocouple.get_value()
    now = time_module.DateTime()
    nowstr = '{hour}:{minute}:{second}'.format(
        hour=leading_zero(now[4]),
        minute=leading_zero(now[5]),
        second=leading_zero(now[6]))

    data_str = '{time}; {thermocouple_temp}; {raw_temperature}; {temperature}; {raw_delta}; {delta}; {fan_speed}; {pid_speed}; {p_part}; {i_part}; {d_part}'.format(
        time=nowstr,
        thermocouple_temp=to_log_value(thermocouple_temp),
        raw_temperature=to_log_value(tempsensor.current_raw_temperature),
        temperature=to_log_value(tempsensor.current_temperature),
        raw_delta=to_log_value(tempsensor.current_raw_delta),
        delta=to_log_value(tempsensor.current_delta),
        fan_speed=to_log_value(fan.current_speed),
        pid_speed=to_log_value(fan_controller.speed),
        p_part=to_log_value(fan_controller.proportional_part),
        i_part=to_log_value(fan_controller.integral_part),
        d_part=to_log_value(fan_controller.derivative_part)
    )

    print(data_str)

    with open(filename, 'a') as file:
        file.write(data_str)
        file.write('\n')


def main():
    main_timer.init(period=50, mode=Timer.PERIODIC, callback=tick)


if __name__ == '__main__':
    main()
