class PWMHAL:
    def __init__(self, config=None, logger=None):
        self.config = config or {}
        self.logger = logger
        self._channels = {}
        try:
            import machine
            self._machine = machine
        except Exception:
            self._machine = None

    def set(self, pin, freq=1000, duty=512):
        if not self._machine:
            return
        if pin not in self._channels:
            self._channels[pin] = self._machine.PWM(self._machine.Pin(pin))
        pwm = self._channels[pin]
        pwm.freq(freq)
        pwm.duty(duty)
