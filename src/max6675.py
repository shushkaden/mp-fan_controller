import time


class MAX6675:
    MEASUREMENT_PERIOD_MS = 220

    def __init__(self, sck, cs, so):
        """
        Creates new object for controlling MAX6675
        :param sck: SCK (clock) pin, must be configured as Pin.OUT
        :param cs: CS (select) pin, must be configured as Pin.OUT
        :param so: SO (data) pin, must be configured as Pin.IN
        """
        # Thermocouple
        self._sck = sck
        self._sck.off()

        self._cs = cs
        self._cs.on()

        self._so = so
        self._so.off()

        self._last_measurement_start = 0
        self._last_read_temp = 0

    def ready(self):
        """
        Signals if measurement is finished.
        :return: True if measurement is ready for reading.
        """
        return time.ticks_ms() - self._last_measurement_start > MAX6675.MEASUREMENT_PERIOD_MS

    def read(self):
        """
        Reads last measurement and starts a new one. If new measurement is not ready yet, returns last value.
        Note: The last measurement can be quite old (e.g. since last call to `read`).
        :return: Measured temperature
        """
        # Check if new reading is available
        if not self.ready():
            return self._last_read_temp

        bits = []
        temp = 0
        self._cs.off()
        time.sleep(0.001)

        for i in range(16):
            self._sck.off()
            time.sleep(0.001)
            bbb = self._so.value()
            bits.append(str(bbb))
            self._sck.on()

        self._cs.on()
        ll = bits[:13]

        for i in range(0, 13):
            temp += int(ll[-i - 1]) * pow(2, i)

        if temp == 4095:
            return -1

        temp /= 4
        self._last_read_temp = temp
        self._last_measurement_start = time.ticks_ms()
        return temp
