APP_NAME = "home"
APP_VERSION = "1.0"
PRIORITY = "high"

_kernel = None


def on_start(kernel):
    global _kernel
    _kernel = kernel

    def _on_tick(payload):
        count = (payload or {}).get("count", 0)
        try:
            _kernel.state.set("tick_count", count, persist=True)
            if count % 5 == 0:
                _kernel.bus.post("storage:write_config", {"last_tick_checkpoint": count})
        except Exception as exc:
            _kernel.logger.warn("home tick handler failed: %s" % exc)

    kernel.bus.on("timer:tick", _on_tick)
    kernel.logger.info("home app started")


def on_resume(state):
    if _kernel:
        _kernel.logger.info("home resumed")


def on_pause(state):
    if _kernel:
        _kernel.logger.info("home paused")


def on_stop():
    return None


def run(state, bus):
    if _kernel and _kernel.hal and _kernel.hal.display:
        # Display APIs are no-op by default but keep flow consistent.
        _kernel.hal.display.clear()
        _kernel.hal.display.draw_text(0, 0, "uOS Home")
        _kernel.hal.display.draw_text(0, 12, "ticks: %s" % state.get("tick_count", 0))
        _kernel.hal.display.show()
    return None
