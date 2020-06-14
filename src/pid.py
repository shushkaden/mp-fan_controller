import time

from smooth import SmoothValue


class PIDFanTempController:
    pwm_fan = None
    temp_sensor = None

    proportional_part = 0
    integral_part = 0
    derivative_part = 0
    target_temperature = 70
    predicted_speed = 10
    proportional_ratio = 15  # percents/degree
    integral_ratio = 0.2  # percents/(degree*second)
    derivative_ratio = 30  # percents/(degree/second)
    derivative_part_delay = 5  # delay in seconds for derivative part
    integral_part_active = False
    speed = 0
    max_integration_part = 105
    min_integration_part = -30

    smooth_delta = SmoothValue(0.1, 1, 1)
    smooth_derivative_delta = SmoothValue(0.1, 1, 1)

    temp_values = []

    def __init__(self, pwm_fan, temp_sensor):
        self.pwm_fan = pwm_fan
        self.temp_sensor = temp_sensor

    def update_fan_speed(self):
        self.update_temp_data()
        self.speed = self.get_new_fan_speed()
        fan_speed = round(self.speed * 1023 / 100)
        self.pwm_fan.set_speed(fan_speed)

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

        current_delta = self.smooth_delta.get_smooth(self.temp_values[-1]['temperature'] - self.target_temperature)

        # proportional part
        self.proportional_part = self.proportional_ratio * current_delta + self.predicted_speed

        # integral part
        if self.integral_part_active and len(self.temp_values) >= 2:
            self.integral_part += self.integral_ratio * (current_delta * (self.temp_values[-1]['time'] - self.temp_values[-2]['time']))
            self.integral_part = min(self.integral_part, self.max_integration_part)
            self.integral_part = max(self.integral_part, self.min_integration_part)

        # derivative part
        if len(self.temp_values) >= 2:
            derivative_temperature_delta = self.smooth_derivative_delta.get_smooth(self.temp_values[-1]['temperature'] - self.temp_values[0]['temperature'])
            derivative_time_delta = self.temp_values[-1]['time'] - self.temp_values[0]['time']
            derivative_delta = derivative_temperature_delta / derivative_time_delta
            self.derivative_part = self.derivative_ratio * derivative_delta

        fan_speed = self.proportional_part + self.integral_part + self.derivative_part

        fan_speed = max(fan_speed, 0)
        fan_speed = min(fan_speed, 100)

        return fan_speed
