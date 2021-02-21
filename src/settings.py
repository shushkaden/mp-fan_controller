SD_CARD_PATH = '/sd'

DATA_LOGGER = {
    'dir': 'sensor_log',
    'use_sd': True,
}

LOGGING_FILE = '/logs/log.log'

FAN = {
    'min_speed': 360,
    'turn_on_speed': 370,
    'turn_off_speed': 350,
    'starting_speed': 450,
    'starting_time': 1000,
    'pwm_frequency': 100000,
    'min_fan_speed': 350,
}

TICK_PERIOD = 50  # milliseconds
OPERATIONAL_PERIOD = 1000  # milliseconds

OPERATIONAL_FREQUENCY = int(OPERATIONAL_PERIOD/TICK_PERIOD)

TARGET_TEMPERATURE = 70

PINS = {
    'fan': 12,
    'fan_led': 13,
    'test_toggle': 27,
    'full_throttle_toggle': 26,
    'tempsensor': 32,
    'tempsensor_aux': 33,
    'buzzer': 10,
}