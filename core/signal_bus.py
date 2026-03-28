class SignalBus:
    def __init__(self, logger=None):
        self.logger = logger
        self._listeners = {}
        self._queue = []

    def on(self, event_name, callback):
        callbacks = self._listeners.get(event_name, [])
        callbacks.append(callback)
        self._listeners[event_name] = callbacks

    def post(self, event_name, data=None):
        self._queue.append((event_name, data))

    def dispatch(self):
        queue = self._queue
        self._queue = []
        for event_name, data in queue:
            callbacks = self._listeners.get(event_name, [])
            for callback in callbacks:
                try:
                    callback(data)
                except Exception as exc:
                    if self.logger:
                        self.logger.warn("bus callback failed: %s" % exc)
