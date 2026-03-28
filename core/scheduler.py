try:
    import utime as time
except ImportError:
    import time


class Scheduler:
    def __init__(self, logger=None):
        self.logger = logger
        self._background = []

    def add_background_task(self, name, callback, interval_ms=1000, priority=50):
        self._background.append(
            {
                "name": name,
                "callback": callback,
                "interval_ms": interval_ms,
                "last_ms": 0,
                "priority": priority,
                "active": True,
            }
        )

    def kill_lowest_priority(self):
        active = [t for t in self._background if t["active"]]
        if not active:
            return None
        victim = sorted(active, key=lambda t: t["priority"])[0]
        victim["active"] = False
        if self.logger:
            self.logger.warn("task stopped due memory pressure: %s" % victim["name"])
        return victim["name"]

    def run_foreground_tick(self, app, state, bus):
        if app and hasattr(app, "run"):
            return app.run(state, bus)
        return None

    def _now_ms(self):
        try:
            return time.ticks_ms()
        except Exception:
            return int(time.time() * 1000)

    def _elapsed(self, now_ms, last_ms):
        try:
            return time.ticks_diff(now_ms, last_ms)
        except Exception:
            return now_ms - last_ms

    def run_background_ticks(self):
        now_ms = self._now_ms()
        for task in self._background:
            if not task["active"]:
                continue
            if task["last_ms"] == 0 or self._elapsed(now_ms, task["last_ms"]) >= task["interval_ms"]:
                try:
                    task["callback"]()
                except Exception as exc:
                    if self.logger:
                        self.logger.warn("task %s failed: %s" % (task["name"], exc))
                task["last_ms"] = now_ms
