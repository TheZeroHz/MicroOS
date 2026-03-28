class DisplayHAL:
    def __init__(self, config=None, logger=None):
        self.config = config or {}
        self.logger = logger

    def clear(self):
        return None

    def draw_text(self, x, y, text):
        _ = (x, y, text)
        return None

    def show(self):
        return None
