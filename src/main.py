import uos
from machine import SDCard, Timer, reset, RTC

import settings

from button import Toggle
from buzzer import Buzzer
from data_logger import CSVDataLogger
from logging import basicConfig, getLogger
from pwmfan import PWMFan
from pid import PIDFanTempController
from tempsensor import Tempsensor
from time import now
from utils import leading_zero, to_log_value

PERIOD = 50

# init logging
basicConfig(filename=settings.LOGGING_FILE, format="{asctime} {message}", style="{")
logger = getLogger()
logger.info('STARTING...')


def log_and_restart(e):
    logger.exc(e, 'ERROR OCCURRED')
    logger.info('RESTARTING...')
    reset()


def log_and_restart_decorator(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log_and_restart(e)
    return wrapper


try:
    logger.info('Initialize hardware')

    # init time
    RTC().datetime(tuple(now() + [0]))

    # mount sd card
    uos.mount(SDCard(slot=2, sck=18, miso=19, mosi=23, cs=5), settings.SD_CARD_PATH)

    # init buzzer
    buzzer = Buzzer(10)

    # init sensors and fan
    tempsensor = Tempsensor(pin=32)
    fan = PWMFan()
    fan_controller = PIDFanTempController(fan, tempsensor, buzzer, 70)

    # init buttons
    Toggle(pin=36, action=fan.full_throttle, cancel_action=fan.auto)

    # init data logger
    data_logger = CSVDataLogger(['time', 'temp', 'speed'])

    # init timer
    main_timer = Timer(-1)
    counter = 0

    logger.info('Initialization complete')
except Exception as e:
    log_and_restart(e)


@log_and_restart_decorator
def tick(timer):
    global counter
    counter += 1

    if counter == 20:
        tempsensor.get_temperature()
        fan_controller.update_fan_speed()
        log_sensors_data()
        counter = 0

    tempsensor.tick()
    fan.tick(PERIOD)
    buzzer.tick(PERIOD)


def log_sensors_data():
    time_now = now()
    nowstr = '{hour}:{minute}:{second}'.format(
        hour=leading_zero(time_now[4]),
        minute=leading_zero(time_now[5]),
        second=leading_zero(time_now[6]))

    data_logger.log_data({
        'time': nowstr,
        'temp': to_log_value(tempsensor.current_temperature),
        'speed': to_log_value(fan.current_speed),
    })


def main():
    main_timer.init(period=PERIOD, mode=Timer.PERIODIC, callback=tick)


if __name__ == '__main__':
    main()
