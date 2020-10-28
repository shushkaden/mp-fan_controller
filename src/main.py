import time
import uos
from machine import Pin, PWM, SDCard, Timer, reset, RTC

import settings

from button import Toggle
from buzzer import Buzzer
from data_logger import CSVDataLogger
from logging import basicConfig, getLogger
from pwmfan import PWMFan
from pid import PIDFanTempController
from tempsensor import Tempsensor
from timemodule import now
from utils import leading_zero, to_log_value


# safe mode
# used if there is an error
full_throttle_pin = Pin(settings.PINS['full_throttle_toggle'], Pin.IN)
fan_pin = None
while full_throttle_pin.value():
    if not fan_pin:
        fan_pin = PWM(Pin(settings.PINS['fan']), 100)
        fan_pin.duty(1023)
    time.sleep(1)
# safe mode

# init logging
basicConfig(filename=settings.LOGGING_FILE, format="{asctime} {message}", style="{")
logger = getLogger()
logger.info('STARTING...')
buzzer = None


def log_and_restart(e):
    logger.exc(e, 'ERROR OCCURRED')
    logger.info('RESTARTING...')
    if buzzer is not None:
        try:
            buzzer.play_error_signal()
        except:
            pass
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
    buzzer = Buzzer(pin=settings.PINS['buzzer'])

    # init sensors and fan
    tempsensor = Tempsensor(pin=settings.PINS['tempsensor'])
    fan = PWMFan(pin=settings.PINS['fan'], led_pin=settings.PINS['fan_led'])
    fan_controller = PIDFanTempController(fan, tempsensor, buzzer, settings.TARGET_TEMPERATURE)

    # init buttons
    # full throttle
    Toggle(pin=settings.PINS['full_throttle_toggle'], action=fan.full_throttle, cancel_action=fan.auto)
    # test
    Toggle(pin=settings.PINS['test_toggle'], action=buzzer.test_on, cancel_action=buzzer.test_off)

    # init data logger
    data_logger = CSVDataLogger(['time', 'temp', 'speed'])

    # init timer
    main_timer = Timer(-1)
    operational_counter = 0

    logger.info('Initialization complete')
    buzzer.play_turn_on_signal()
except Exception as e:
    log_and_restart(e)


@log_and_restart_decorator
def tick(timer):
    buzzer.tick(settings.TICK_PERIOD)
    tempsensor.tick()
    fan.tick(settings.TICK_PERIOD)

    global operational_counter
    operational_counter += 1
    
    if operational_counter == settings.OPERATIONAL_FREQUENCY:
        tempsensor.get_temperature()
        fan_controller.update_fan_speed()
        log_sensors_data()
        operational_counter = 0


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
    main_timer.init(period=settings.TICK_PERIOD, mode=Timer.PERIODIC, callback=tick)


if __name__ == '__main__':
    main()
