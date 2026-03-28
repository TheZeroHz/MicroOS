import gc


class MemoryManager:
    GREEN = 50 * 1024
    YELLOW = 20 * 1024
    RED = 20 * 1024

    def __init__(self, logger=None):
        self.logger = logger

    def collect(self):
        gc.collect()
        try:
            return gc.mem_free()
        except Exception:
            # Host-side fallback for non-MicroPython test runs.
            return 999999

    def check(self):
        free_mem = self.collect()
        if free_mem > self.GREEN:
            return "green", free_mem
        if free_mem > self.YELLOW:
            return "yellow", free_mem
        return "red", free_mem
