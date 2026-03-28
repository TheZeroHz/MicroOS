class I2CHAL:
    def __init__(self, config=None, logger=None):
        self.config = config or {}
        self.logger = logger
        self._i2c = None
        try:
            import machine
            pins = self.config.get("pins", {})
            self._i2c = machine.I2C(
                0,
                scl=machine.Pin(pins.get("scl", 22)),
                sda=machine.Pin(pins.get("sda", 21)),
            )
        except Exception:
            self._i2c = None

    def scan(self):
        if not self._i2c:
            return []
        return self._i2c.scan()
