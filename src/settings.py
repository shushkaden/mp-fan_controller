SD_CARD_PATH = '/sd'

DATA_LOGGER = {
    'dir': 'sensor_log',
    'use_sd': True,
}

LOGGING_FILE = '/logs/log.txt'

FAN = {
    'turn_on_speed': 90,
    'turn_off_speed': 80,
    'min_speed': 85,
    'starting_speed': 100,
    'starting_time': 500,
    'pwm_frequency': 440,
}

TICK_PERIOD = 50  # milliseconds
OPERATIONAL_PERIOD = 1000  # milliseconds

OPERATIONAL_FREQUENCY = int(OPERATIONAL_PERIOD/TICK_PERIOD)

TARGET_TEMPERATURE = 80

PINS = {
    'fan': 12,
    'fan_led': 13,
    'test_toggle': 27,
    'full_throttle_toggle': 26,
    'tempsensor': 33,
    'tempsensor_aux': 32,
    'buzzer': 10,
}