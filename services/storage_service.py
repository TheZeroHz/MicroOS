try:
    import ujson as json
except ImportError:
    import json


class StorageService:
    name = "storage_service"
    interval_ms = 0
    priority = 90

    def __init__(self, kernel):
        self.kernel = kernel

    def start(self):
        self.kernel.bus.on("storage:write_config", self._on_write_config)
        self.kernel.bus.on("storage:write_state", self._on_write_state)
        self.kernel.logger.info("storage service started")

    def tick(self):
        return None

    def _on_write_config(self, payload):
        patch = payload or {}
        self.kernel.config.update(patch)
        try:
            with open("data/config.json", "w") as f:
                f.write(json.dumps(self.kernel.config))
        except Exception as exc:
            self.kernel.logger.warn("storage config write failed: %s" % exc)

    def _on_write_state(self, payload):
        try:
            self.kernel.state.update(payload or {}, persist=True)
        except Exception as exc:
            self.kernel.logger.warn("storage state write failed: %s" % exc)
