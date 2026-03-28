try:
    import ujson as json
except ImportError:
    import json

try:
    import utime as time
except ImportError:
    import time


class Logger:
    def __init__(
        self,
        logs_dir="data/logs",
        max_entries=200,
        max_file_bytes=32768,
        backup_count=2,
    ):
        self.logs_dir = logs_dir
        self.max_entries = max_entries
        self.max_file_bytes = max_file_bytes
        self.backup_count = backup_count
        self._buffer = []
        self._file_path = logs_dir + "/latest.log"
        self._ensure_logs_dir()

    def _ensure_logs_dir(self):
        try:
            import os
            os.mkdir(self.logs_dir)
        except Exception:
            pass

    def _stamp(self):
        try:
            return str(time.ticks_ms())
        except Exception:
            return str(int(time.time() * 1000))

    def _write(self, level, message):
        row = {"ts": self._stamp(), "level": level, "msg": str(message)}
        self._buffer.append(row)
        if len(self._buffer) > self.max_entries:
            self._buffer.pop(0)
        try:
            self._rotate_if_needed()
            with open(self._file_path, "a") as f:
                f.write(json.dumps(row) + "\n")
        except Exception:
            pass

    def _rotate_if_needed(self):
        if not self.max_file_bytes or self.max_file_bytes <= 0:
            return
        try:
            import os
            size = os.stat(self._file_path)[6]
        except Exception:
            size = 0
        if size < self.max_file_bytes:
            return
        try:
            import os
            for idx in range(self.backup_count, 0, -1):
                src = "%s.%d" % (self._file_path, idx - 1) if idx > 1 else self._file_path
                dst = "%s.%d" % (self._file_path, idx)
                try:
                    os.rename(src, dst)
                except Exception:
                    pass
        except Exception:
            pass

    def info(self, message):
        self._write("INFO", message)

    def warn(self, message):
        self._write("WARN", message)

    def error(self, message):
        self._write("ERROR", message)

    def recent(self):
        return list(self._buffer)
