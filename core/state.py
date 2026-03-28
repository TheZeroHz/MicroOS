try:
    import ujson as json
except ImportError:
    import json


class StateStore:
    def __init__(self, state_path="data/state.json", allowed_keys=None, logger=None):
        self.state_path = state_path
        self.allowed_keys = allowed_keys or []
        self.logger = logger
        self._state = {}
        self._load()

    def _log(self, method, message):
        if self.logger:
            getattr(self.logger, method, self.logger.info)(message)

    def _load(self):
        try:
            with open(self.state_path, "r") as f:
                self._state = json.loads(f.read() or "{}")
        except Exception:
            self._state = {}

    def snapshot(self):
        return dict(self._state)

    def get(self, key, default=None):
        return self._state.get(key, default)

    def set(self, key, value, persist=False):
        if self.allowed_keys and key not in self.allowed_keys:
            raise KeyError("Key not allowed: %s" % key)
        self._state[key] = value
        if persist:
            self.persist()

    def update(self, values, persist=False):
        for key, value in values.items():
            self.set(key, value, persist=False)
        if persist:
            self.persist()

    def persist(self):
        try:
            with open(self.state_path, "w") as f:
                f.write(json.dumps(self._state))
        except Exception as exc:
            self._log("warn", "state persist failed: %s" % exc)
