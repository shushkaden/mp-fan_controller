from machine import Pin, PWM

import settings


class PWMFan:

    def __init__(self, pin=12, led_pin=None):
        self.fan_pin = PWM(Pin(pin), self.pwm_frequency)
        self._set_speed(0)
        self.led_pin = None
        if led_pin:
            self.led_pin = Pin(led_pin, Pin.OUT)
            self.led_pin.value(0)

        self.turn_on_speed = settings.FAN['turn_on_speed']  # Fan starts if set speed is higher then $turn_on_speed
        self.turn_off_speed = settings.FAN['turn_off_speed']  # Fan stops if set speed is lower then $turn_off_speed
        self.min_speed = settings.FAN['min_speed']  # Fan rotates with $min_speed even if set speed is lower
        self.starting_speed = settings.FAN['starting_speed']  # Fan starts with $starting_speed during $starting_time
        self.starting_time = settings.FAN['starting_time']
        self.pwm_frequency = settings.FAN['pwm_frequency']
        self.current_speed = 0
        self.is_running = False
        self.is_starting = False
        self.counter = 0
        self.full_throttle_mode = False

    def _start(self):
        self.is_running = True
        self.is_starting = True
        self._set_speed(self.starting_speed)

    def _stop(self):
        self.is_running = False
        self._set_speed(0)

    def tick(self, miliseconds):
        if self.led_pin:
            self.led_pin.value(int(self.is_running))

        if self.full_throttle_mode:
            return

        if not self.is_starting:
            return

        self.counter += miliseconds
        if self.counter >= self.starting_time:
            self.counter = 0
            self._set_speed(self.turn_on_speed)
            self.is_starting = False

    def full_throttle(self):
        self.full_throttle_mode = True
        self.is_running = True
        self.is_starting = False
        self._set_speed(1023)

    def auto(self):
        self.full_throttle_mode = False

    @property
    def _can_change_speed(self):
        return not self.is_starting and not self.full_throttle_mode

    def _set_speed(self, speed):
        speed = min(speed, 1023)
        speed = round(max(speed, 0))
        self.current_speed = speed
        self.fan_pin.duty(speed)

    def set_speed_percent(self, speed):
        speed = min(speed, 100)
        speed = max(speed, 0)
        if speed == 0:
            return self.set_speed(speed)
        fan_range = 1023 - self.min_speed
        speed = self.min_speed + fan_range * speed / 100
        return self.set_speed(speed)


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
