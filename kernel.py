try:
    import ujson as json
except ImportError:
    import json

try:
    import utime as time
except ImportError:
    import time

from core.logger import Logger
from core.state import StateStore
from core.signal_bus import SignalBus
from core.navigator import Navigator
from core.scheduler import Scheduler
from core.memory import MemoryManager
from core.watchdog import Watchdog
from core.ipc import IPCPipe

from hal.hal import HAL

from services.timer_service import TimerService
from services.storage_service import StorageService
from services.wifi_service import WifiService
from services.ota_service import OTAService
from services.mqtt_service import MQTTService

import apps.home as app_home
import apps.settings as app_settings
import apps.wifi_app as app_wifi


BOOTING = "BOOTING"
INIT_HARDWARE = "INIT_HARDWARE"
INIT_SERVICES = "INIT_SERVICES"
RUNNING = "RUNNING"
SWITCHING_APP = "SWITCHING_APP"
APP_RUNNING = "APP_RUNNING"
PANIC = "PANIC"


class Kernel:
    def __init__(self):
        self.phase = BOOTING
        self.config = self._load_config()
        self.logger = Logger(
            logs_dir=self.config.get("logs_dir", "data/logs"),
            max_entries=self.config.get("log_buffer_entries", 200),
            max_file_bytes=self.config.get("log_max_file_bytes", 32768),
            backup_count=self.config.get("log_backup_count", 2),
        )
        self.state = StateStore(
            state_path="data/state.json",
            allowed_keys=self.config.get("state_allowed_keys", []),
            logger=self.logger,
        )
        self.bus = SignalBus(logger=self.logger)
        self.navigator = Navigator(logger=self.logger)
        self.scheduler = Scheduler(logger=self.logger)
        self.memory = MemoryManager(logger=self.logger)
        self.watchdog = Watchdog(
            timeout_ms=self.config.get("watchdog_timeout_ms", 8000),
            logger=self.logger,
            enabled=self.config.get("watchdog_enabled", False),
        )
        self.ipc = IPCPipe(logger=self.logger)
        self.hal = None
        self.services = []
        self._running = True

    def _load_config(self):
        default = {
            "board": "esp32",
            "watchdog_enabled": False,
            "watchdog_timeout_ms": 8000,
            "main_loop_sleep_ms": 50,
            "uart_enabled": False,
            "uart_id": 1,
            "uart_baudrate": 115200,
            "logs_dir": "data/logs",
            "log_buffer_entries": 200,
            "log_max_file_bytes": 32768,
            "log_backup_count": 2,
            "state_allowed_keys": [
                "wifi_connected",
                "tick_count",
                "current_app",
                "last_error",
                "settings",
            ],
            "pins": {"sda": 21, "scl": 22, "led": 2},
        }
        try:
            with open("data/config.json", "r") as f:
                loaded = json.loads(f.read() or "{}")
            default.update(loaded)
        except Exception:
            pass
        return default

    def _persist_config(self):
        try:
            with open("data/config.json", "w") as f:
                f.write(json.dumps(self.config))
        except Exception as exc:
            self.logger.warn("config persist failed: %s" % exc)

    def _init_hal(self):
        self.phase = INIT_HARDWARE
        self.hal = HAL(self.config, logger=self.logger)
        self.hal.init_all()

    def _register_apps(self):
        for name, app in (
            ("home", app_home),
            ("settings", app_settings),
            ("wifi_app", app_wifi),
        ):
            if hasattr(app, "on_start"):
                app.on_start(self)
            self.navigator.register(name, app)

    def _start_services(self):
        self.phase = INIT_SERVICES
        storage = StorageService(self)
        timer = TimerService(self)
        wifi = WifiService(self)
        ota = OTAService(self)
        mqtt = MQTTService(self)
        self.services = [storage, timer, wifi, ota, mqtt]
        for service in self.services:
            service.start()
            if service.interval_ms > 0:
                self.scheduler.add_background_task(
                    service.name,
                    service.tick,
                    interval_ms=service.interval_ms,
                    priority=service.priority,
                )

    def _setup_bus(self):
        def on_app_switch(payload):
            target = (payload or {}).get("app")
            if not target:
                return
            self.phase = SWITCHING_APP
            self.memory.collect()
            self.navigator.navigate(target, self.state)
            self.state.set("current_app", target, persist=True)
            self.phase = APP_RUNNING

        self.bus.on("nav:goto", on_app_switch)

    def _launch_home(self):
        self.navigator.replace("home", self.state)
        self.state.set("current_app", "home", persist=True)

    def _sleep_ms(self, value):
        try:
            time.sleep_ms(value)
        except Exception:
            time.sleep(value / 1000.0)

    def run(self, max_cycles=None):
        self.logger.info("kernel boot")
        self._persist_config()
        self._init_hal()
        self._register_apps()
        self._setup_bus()
        self._start_services()
        self._launch_home()
        self.phase = RUNNING

        cycles = 0
        while self._running:
            try:
                current_app = self.navigator.current()
                self.phase = APP_RUNNING
                self.scheduler.run_foreground_tick(current_app, self.state, self.bus)
                self.scheduler.run_background_ticks()
                self.bus.dispatch()

                zone, free_mem = self.memory.check()
                if zone == "red":
                    self.logger.warn("low memory red: %s" % free_mem)
                    self.scheduler.kill_lowest_priority()

                self.watchdog.feed()
                self._sleep_ms(self.config.get("main_loop_sleep_ms", 50))
            except KeyboardInterrupt:
                self.logger.warn("kernel interrupted by user")
                self._running = False
            except Exception as exc:
                self.phase = PANIC
                self.logger.error("kernel loop error: %s" % exc)
                self.state.set("last_error", str(exc), persist=True)
                try:
                    self.navigator.replace("home", self.state)
                except Exception:
                    pass
                self.phase = RUNNING
            finally:
                cycles += 1
                if max_cycles is not None and cycles >= max_cycles:
                    self._running = False


def start():
    Kernel().run()
