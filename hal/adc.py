class ADCHAL:
    def __init__(self, config=None, logger=None):
        self.config = config or {}
        self.logger = logger
        try:
            import machine
            self._machine = machine
        except Exception:
            self._machine = None

    def read_raw(self, pin):
        if not self._machine:
            return 0
        adc = self._machine.ADC(self._machine.Pin(pin))
        return adc.read()
