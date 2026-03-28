class SPIHAL:
    def __init__(self, config=None, logger=None):
        self.config = config or {}
        self.logger = logger
        self._spi = None
        try:
            import machine
            self._spi = machine.SPI(1)
        except Exception:
            self._spi = None
