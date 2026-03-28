class MQTTService:
    name = "mqtt_service"
    interval_ms = 3000
    priority = 50

    def __init__(self, kernel):
        self.kernel = kernel
        self.connected = False

    def start(self):
        self.kernel.logger.info("mqtt service started")
        self.kernel.bus.post("mqtt:status", {"connected": self.connected})

    def tick(self):
        # Placeholder broker health check.
        self.kernel.bus.post("mqtt:status", {"connected": self.connected})
