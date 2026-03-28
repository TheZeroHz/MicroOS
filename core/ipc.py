class IPCPipe:
    def __init__(self, logger=None):
        self.logger = logger
        self._queue = []

    def send(self, topic, payload=None):
        self._queue.append((topic, payload))

    def recv_all(self):
        items = self._queue
        self._queue = []
        return items
