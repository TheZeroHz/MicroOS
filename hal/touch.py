class TouchHAL:
    def __init__(self, config=None, logger=None):
        self.config = config or {}
        self.logger = logger

    def read_points(self):
        return []
