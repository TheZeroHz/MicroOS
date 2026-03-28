class Navigator:
    def __init__(self, logger=None):
        self.logger = logger
        self._registry = {}
        self._stack = []
        self._current = None

    def register(self, name, app_module):
        self._registry[name] = app_module

    def stack(self):
        return list(self._stack)

    def current(self):
        return self._current

    def _call(self, app, method_name, *args):
        if app and hasattr(app, method_name):
            try:
                return getattr(app, method_name)(*args)
            except Exception as exc:
                if self.logger:
                    self.logger.warn("app %s failed: %s" % (method_name, exc))
        return None

    def navigate(self, name, state):
        app = self._registry.get(name)
        if not app:
            raise KeyError("Unknown app: %s" % name)
        if self._current:
            self._call(self._current, "on_pause", state)
        self._stack.append(name)
        self._current = app
        self._call(self._current, "on_resume", state)
        return self._current

    def replace(self, name, state):
        if self._current:
            self._call(self._current, "on_pause", state)
        self._stack = [name]
        self._current = self._registry.get(name)
        if not self._current:
            raise KeyError("Unknown app: %s" % name)
        self._call(self._current, "on_resume", state)
        return self._current

    def go_back(self, state):
        if len(self._stack) <= 1:
            return self._current
        current_name = self._stack.pop()
        previous_name = self._stack[-1]
        current_app = self._registry.get(current_name)
        prev_app = self._registry.get(previous_name)
        self._call(current_app, "on_pause", state)
        self._current = prev_app
        self._call(self._current, "on_resume", state)
        return self._current
