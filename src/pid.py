import time

from smooth import SmoothValue


class PIDFanTempController:
    pwm_fan = None
    temp_sensor = None

    integral_part = 0
    target_temperature = 80
    proportional_ratio = 8  # percents/degree
    integral_ratio = 0.5  # percents/(degree*second)
    derivative_ratio = 100  # percents/(degree/second)
    derivative_part_delay = 5  # delay in seconds for derivative part
    integral_part_active = False

    temp_values = []

    def __init__(self, pwm_fan, temp_sensor):
        self.pwm_fan = pwm_fan
        self.temp_sensor = temp_sensor

    def update_fan_speed(self):
        self.update_temp_data()
        speed = self.get_new_fan_speed()
        speed = round(speed * 1023 / 100)
        self.pwm_fan.set_speed(speed)

    def update_temp_data(self):
        temperature = self.temp_sensor.current_temperature
        # use integration part only when target temperature is reached
        self.integral_part_active = self.integral_part_active or temperature >= self.target_temperature
        self.temp_values.append({'temperature': temperature, 'time': time.time()})
        while len(self.temp_values) > self.derivative_part_delay + 1:
            self.temp_values.pop(0)

    def get_new_fan_speed(self):
        if not len(self.temp_values):
            return 0

        current_delta = self.temp_values[-1]['temperature'] - self.target_temperature

        # proportional part
        proportional_part = self.proportional_ratio * current_delta

        # integral part
        if self.integral_part_active and len(self.temp_values) >= 2:
            self.integral_part += current_delta * (self.temp_values[-1]['time'] - self.temp_values[-2]['time'])

        # derivative part
        derivative_temperature_delta = self.temp_values[-1]['temperature'] - self.temp_values[0]['temperature']
        derivative_time_delta = self.temp_values[-1]['time'] - self.temp_values[0]['time']
        derivative_delta = derivative_temperature_delta / derivative_time_delta
        derivative_part = self.derivative_ratio * derivative_delta

        fan_speed = proportional_part + self.integral_part + derivative_part

        fan_speed = max(fan_speed, 0)
        fan_speed = min(fan_speed, 100)

        return fan_speed






