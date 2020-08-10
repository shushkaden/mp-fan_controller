from machine import Pin, PWM

import settings


class PWMFan:
    min_speed = settings.FAN['min_speed']
    turn_on_speed = settings.FAN['turn_on_speed']
    turn_off_speed = settings.FAN['turn_off_speed']
    starting_speed = settings.FAN['starting_speed']
    starting_time = settings.FAN['starting_time']
    pwm_frequency = settings.FAN['pwm_frequency']
    fan_pin = None
    current_speed = 0
    is_running = False
    is_starting = False
    counter = 0

    def __init__(self, pin=12):
        self.fan_pin = PWM(Pin(pin), self.pwm_frequency)

    def _start(self):
        self.is_running = True
        self.is_starting = True
        self._set_speed(self.starting_speed)

    def _stop(self):
        self.is_running = False
        self._set_speed(0)

    def tick(self, miliseconds):
        if not self.is_starting:
            return

        self.counter += miliseconds
        if self.counter >= self.starting_time:
            self.counter = 0
            self._set_speed(self.turn_on_speed)
            self.is_starting = False

    @property
    def _can_change_speed(self):
        return not self.is_starting

    def _set_speed(self, speed):
        self.current_speed = speed
        self.fan_pin.duty(speed)

    def set_speed(self, speed):
        if not self._can_change_speed:
            return

        if not self.is_running:
            if speed >= self.starting_speed:
                self.is_running = True
                self._set_speed(speed)
                return

            if speed >= self.turn_on_speed:
                self._start()
                return

        if self.is_running:
            if speed < self.turn_off_speed:
                self._stop()
                return

            speed = max(speed, self.min_speed)
            self._set_speed(speed)
