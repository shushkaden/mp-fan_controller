from machine import Pin, PWM


class Buzzer:
    buzzer = None
    low_freq = None
    high_freq = None
    freq = None
    active = False
    timer = 0

    def __init__(self, pin=10, low_freq=250, high_freq=1000, freq=800):
        self.buzzer = PWM(Pin(pin))
        self.low_freq = low_freq
        self.high_freq = high_freq
        self.freq = freq

    def turn_on(self):
        if not self.active:
            self.active = True
            self.buzzer.freq(self.high_freq)
            self.buzzer.duty(1023)
            self.timer = self.freq

    def turn_off(self):
        if self.active:
            self.active = False
            self.buzzer.duty(0)

    def tick(self, miliseconds):
        if not self.active:
            return

        self.timer -= miliseconds
        if self.timer <= 0:
            self.timer += self.freq
            if self.buzzer.freq() == self.low_freq:
                self.buzzer.freq(self.high_freq)
            else:
                self.buzzer.freq(self.low_freq)
