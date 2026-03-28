class OTAService:
    name = "ota_service"
    interval_ms = 15000
    priority = 40

    def __init__(self, kernel):
        self.kernel = kernel

    def start(self):
        self.kernel.logger.info("ota service started")

    def tick(self):
        # Placeholder for periodic OTA check.
        return None
