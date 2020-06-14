from smooth import SmoothValue

class TempsensorMock:
    fan = None
    heater_power = 80
    current_temperature = 60

    current_raw_temperature = 5
    current_raw_delta = 5
    current_delta = 5

    length = 80
    fan_values = []
    smooth_speed = SmoothValue(0.01, 0.1, 20)

    def __init__(self, fan):
        self.fan = fan

    def tick(self):
        fan_speed = self.fan.current_speed * 100 / 1023
        self.fan_values.append(fan_speed)
        while len(self.fan_values) > self.length:
            self.fan_values.pop(0)

        fan_speed = 0
        if len(self.fan_values) == self.length:
            fan_speed = self.fan_values[0]

        self.current_temperature += (self.heater_power - fan_speed) / 5000

    def get_temperature(self):
        pass

    def warm_up(self):
        self.heater_power += 10
        print('HEATER POWER = {}'.format(self.heater_power))

    def cool_down(self):
        self.heater_power = max(0, self.heater_power-10)
        print('HEATER POWER = {}'.format(self.heater_power))

