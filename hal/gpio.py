class GPIOHAL:
    def __init__(self, config=None, logger=None):
        self.config = config or {}
        self.logger = logger
        self._pins = {}
        try:
            import machine
            self._machine = machine
        except Exception:
            self._machine = None

    def write(self, pin, value):
        if not self._machine:
            return
        if pin not in self._pins:
            self._pins[pin] = self._machine.Pin(pin, self._machine.Pin.OUT)
        self._pins[pin].value(1 if value else 0)

    def read(self, pin):
        if not self._machine:
            return 0
        if pin not in self._pins:
            self._pins[pin] = self._machine.Pin(pin, self._machine.Pin.IN)
        return self._pins[pin].value()
