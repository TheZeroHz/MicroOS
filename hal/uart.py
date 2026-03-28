class UARTHAL:
    def __init__(self, config=None, logger=None):
        self.config = config or {}
        self.logger = logger
        self._uart = None
        self._machine = None
        self._uart_id = self.config.get("uart_id", 1)
        self._baudrate = self.config.get("uart_baudrate", 115200)
        self._enabled = bool(self.config.get("uart_enabled", False))
        try:
            import machine
            self._machine = machine
        except Exception:
            self._machine = None

    def _ensure_uart(self):
        if self._uart is not None:
            return self._uart
        if not self._enabled or self._machine is None:
            return None
        try:
            # Avoid UART(0) by default because it is usually reserved for REPL/console.
            self._uart = self._machine.UART(self._uart_id, baudrate=self._baudrate)
        except Exception as exc:
            self._uart = None
            if self.logger:
                self.logger.warn("uart init failed: %s" % exc)
        return self._uart

    def write(self, data):
        uart = self._ensure_uart()
        if uart is None:
            return 0
        try:
            return uart.write(data)
        except Exception:
            return 0

    def read(self, nbytes=None):
        uart = self._ensure_uart()
        if uart is None:
            return None
        try:
            if nbytes is None:
                return uart.read()
            return uart.read(nbytes)
        except Exception:
            return None
