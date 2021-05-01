import time
from machine import Pin


class Buzzer:

    def __init__(self, pin):
        self.pin = Pin(pin, Pin.OUT)
        self.active = False
        self.timer = 0
        self.turn_on_pattern = [0.25]
        self.error_pattern = [1, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]
        self.error_pattern2 = [1, 0.3, 0.2, 0.3, 1, 0.3, 0.2, 0.3, 1, 0.3, 0.2]
        self.alarm_pattern = [0.8, 0.8]
        self.test_pattern = [0.15, 0.15]
        self.repeat_pattern = None
        self.repeat_index = 0

    def turn_on(self):
        if not self.active:
            self.active = True
            self.pin.value(1)

    def turn_off(self):
        if self.active:
            self.active = False
            self.pin.value(0)

    def toggle(self):
        if self.active:
            self.turn_off()
        else:
            self.turn_on()

    def tick(self, milliseconds):
        if not self.repeat_pattern:
            return

        if self.repeat_index is None:  # start from the beginning
            self.turn_off()
            self.repeat_index = -1
            self.timer = 0
        else:
            self.timer -= milliseconds

        if self.timer <= 0:
            self.repeat_index += 1
            self.timer += self.repeat_pattern[self.repeat_index % len(self.repeat_pattern)] * 1000
            self.toggle()

    def play_pattern(self, pattern):
        remember_pattern = self.repeat_pattern
        self.repeat_pattern = None
        self.turn_off()

        for sound_time in pattern:
            self.toggle()
            time.sleep(sound_time)

        self.turn_off()
        self.repeat_index = None
        self.repeat_pattern = remember_pattern

    def play_turn_on_signal(self):
        self.play_pattern(self.turn_on_pattern)

    def play_error_signal(self):
        self.play_pattern(self.error_pattern)

    def play_error2_signal(self):
        self.play_pattern(self.error_pattern2)

    def pattern_on(self, pattern):
        if self.repeat_pattern != pattern:
            self.repeat_index = None
            self.repeat_pattern = pattern

    def alarm_on(self):
        self.pattern_on(self.alarm_pattern)

    def alarm_off(self):
        if self.repeat_pattern == self.alarm_pattern:
            self.turn_off()
            self.repeat_pattern = None

    def test_on(self):
        self.pattern_on(self.test_pattern)

    def test_off(self):
        if self.repeat_pattern == self.test_pattern:
            self.turn_off()
            self.repeat_pattern = None
