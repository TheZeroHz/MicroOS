class Watchdog:
    def __init__(self, timeout_ms=8000, logger=None, enabled=True):
        self.logger = logger
        self._wdt = None
        self.enabled = bool(enabled)
        if not self.enabled:
            if logger:
                logger.info("WDT disabled by config")
            return
        try:
            import machine
            self._wdt = machine.WDT(timeout=timeout_ms)
        except Exception as exc:
            if logger:
                logger.warn("WDT unavailable, using soft mode: %s" % exc)

    def feed(self):
        if self._wdt:
            self._wdt.feed()
