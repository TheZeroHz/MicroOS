APP_NAME = "wifi_app"
APP_VERSION = "1.0"
PRIORITY = "normal"

_kernel = None


def on_start(kernel):
    global _kernel
    _kernel = kernel
    kernel.logger.info("wifi app started")


def on_resume(state):
    if _kernel:
        _kernel.logger.info("wifi app resumed")


def on_pause(state):
    if _kernel:
        _kernel.logger.info("wifi app paused")


def on_stop():
    return None


def run(state, bus):
    return None
