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
data_logger = None


def log_and_restart(e):
    print(str(e))
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

    # init buzzer
    buzzer = Buzzer(pin=settings.PINS['buzzer'])

    # init sensors and fan
    tempsensor = Tempsensor(pin=settings.PINS['tempsensor'])
    tempsensor_aux = Tempsensor(pin=settings.PINS['tempsensor_aux'])
    fan = PWMFan(pin=settings.PINS['fan'], led_pin=settings.PINS['fan_led'])
    fan_controller = PIDFanTempController(fan, tempsensor, buzzer, settings.TARGET_TEMPERATURE)

    # init buttons
    # full throttle
    Toggle(pin=settings.PINS['full_throttle_toggle'], action=fan.full_throttle, cancel_action=fan.auto)
    # test
    Toggle(pin=settings.PINS['test_toggle'], action=buzzer.test_on, cancel_action=buzzer.test_off)

    try:
        # mount sd card
        uos.mount(SDCard(slot=2, sck=18, miso=19, mosi=23, cs=5), settings.SD_CARD_PATH)
    except Exception as e:
        buzzer.play_error2_signal()
        logger.exc(e, 'FLASH CARD ERROR')
    else:
        # init data logger
        data_logger = CSVDataLogger(['time', 'temp', 'temp_aux', 'speed', 'adc', 'adc_value', 'adc_aux', 'adc_value_aux'])

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
    tempsensor_aux.tick()
    fan.tick(settings.TICK_PERIOD)

    global operational_counter
    operational_counter += 1
    
    if operational_counter == settings.OPERATIONAL_FREQUENCY:
        tempsensor.get_temperature()
        tempsensor_aux.get_temperature()
        fan_controller.update_fan_speed()
        log_sensors_data()
        operational_counter = 0


def log_sensors_data():
    time_now = now()
    nowstr = '{hour}:{minute}:{second}'.format(
        hour=leading_zero(time_now[4]),
        minute=leading_zero(time_now[5]),
        second=leading_zero(time_now[6]))

    if data_logger:
        data_logger.log_data({
            'time': nowstr,
            'temp': to_log_value(tempsensor.current_temperature),
            'temp_aux': to_log_value(tempsensor_aux.current_temperature),
            'speed': to_log_value(fan.current_speed),
            'adc': to_log_value(tempsensor.adc_reader.sensor.read()),
            'adc_aux': to_log_value(tempsensor_aux.adc_reader.sensor.read()),
            'adc_value': to_log_value(tempsensor.adc_reader.get_value()),
            'adc_value_aux': to_log_value(tempsensor_aux.adc_reader.get_value()),
        })

    data_str = 'time {time}; temp {temp}; adc {adc}; adc2 {adc2}; aux_temp {aux_temp}; aux_adc {aux_adc}; aux_adc2 {aux_adc2}; speed {speed}'.format(
        time=nowstr,
        temp=to_log_value(tempsensor.current_temperature),
        adc=to_log_value(tempsensor.adc_reader.sensor.read()),
        adc2=to_log_value(tempsensor.adc_reader.get_value()),
        aux_temp=to_log_value(tempsensor_aux.current_temperature),
        aux_adc=to_log_value(tempsensor_aux.adc_reader.sensor.read()),
        aux_adc2=to_log_value(tempsensor_aux.adc_reader.get_value()),
        speed=to_log_value(fan.current_speed),
    )

    print(data_str)


def main():
    main_timer.init(period=settings.TICK_PERIOD, mode=Timer.PERIODIC, callback=tick)


if __name__ == '__main__':
    main()
