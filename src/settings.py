SD_CARD_PATH = '/sd'

DATA_LOGGER = {
    'dir': 'sensor_log',
    'use_sd': True,
}

LOGGING_FILE = '/logs/log.log'

FAN = {
    'min_speed': 10,
    'turn_on_speed': 13,
    'turn_off_speed': 7,
    'starting_speed': 18,
    'starting_time': 1000,
    'pwm_frequency': 100,
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
    'buzzer': 10,
}