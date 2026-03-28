class WifiService:
    name = "wifi_service"
    interval_ms = 5000
    priority = 60

    def __init__(self, kernel):
        self.kernel = kernel
        self.connected = False

    def start(self):
        self.kernel.logger.info("wifi service started")
        self.kernel.bus.post("wifi:status", {"connected": self.connected})

    def tick(self):
        # Placeholder health check loop.
        self.kernel.bus.post("wifi:status", {"connected": self.connected})
