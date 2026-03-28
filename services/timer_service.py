try:
    import utime as time
except ImportError:
    import time


class TimerService:
    name = "timer_service"
    interval_ms = 1000
    priority = 80

    def __init__(self, kernel):
        self.kernel = kernel
        self.tick_count = self.kernel.state.get("tick_count", 0) or 0

    def start(self):
        self.kernel.logger.info("timer service started")

    def tick(self):
        self.tick_count += 1
        payload = {"count": self.tick_count}
        self.kernel.bus.post("timer:tick", payload)
        self.kernel.state.set("tick_count", self.tick_count, persist=True)
