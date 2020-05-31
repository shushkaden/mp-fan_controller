class SmoothValue:
    value = None
    min_value = None
    max_value = None
    divider = None

    def __init__(self, min_value, max_value, divider):
        self.min_value = min_value
        self.max_value = max_value
        self.divider = divider

    def get_smooth(self, value):
        if not self.value:
            self.value = value
            return value

        diff = value - self.value

        smoother = abs(diff)
        smoother /= self.divider
        smoother = max(smoother, self.min_value)
        smoother = min(smoother, self.max_value)

        diff *= smoother

        self.value = self.value + diff

        return self.value
