# µOS (MicroOS) - MicroPython OS Framework

`µOS` is a tiny OS-style framework for MicroPython boards (ESP32-first) that organizes firmware into clear layers: Kernel, Core, HAL, Services, and Apps.

It is designed so apps stay isolated, hardware access stays abstracted, and the system can recover from faults instead of freezing.

## Architecture

```text
Apps -> Services -> Shell/Core Runtime -> Kernel -> HAL -> MicroPython VM -> Hardware
```

Key runtime concepts:
- **Kernel-owned lifecycle**: boot, init hardware/services, launch app, run forever
- **Signal bus**: apps/services communicate with events instead of direct imports
- **Navigator**: stack-based foreground app switching
- **Scheduler**: one foreground tick + periodic background service ticks
- **State store**: RAM + persisted JSON state
- **Memory + watchdog hooks**: basic pressure handling and liveness protection

## Current Status (Phase 3)

Implemented:
- Full scaffold for `core/`, `hal/`, `services/`, `apps/`, `drivers/`, `data/`
- Runnable `boot.py` -> `kernel.start()`
- Core modules: state, signal bus, navigator, scheduler, memory, watchdog, ipc, logger
- HAL contract modules with fail-soft fallbacks when hardware APIs are unavailable
- Service skeletons: wifi/ota/mqtt + functional timer and storage services
- App contract skeletons + functional `home` app vertical slice

Working vertical slice:
- `timer_service` emits `timer:tick`
- `home` app subscribes/reacts
- state/config persistence updates in `data/state.json` and `data/config.json`

## Project Layout

```text
.
├── boot.py
├── kernel.py
├── core/
├── hal/
├── services/
├── drivers/
├── apps/
└── data/
```

## App Contract

Each app module is expected to expose:

```python
APP_NAME = "my_app"
APP_VERSION = "1.0"
PRIORITY = "normal"  # low / normal / high

def on_start(kernel): ...
def on_resume(state): ...
def on_pause(state): ...
def on_stop(): ...
def run(state, bus): ...
```

`run()` should return quickly and avoid blocking IO.

## Quick Start

### 1) Run locally (host smoke run)

From project root:

```bash
python -c "from kernel import Kernel; k=Kernel(); k.run(max_cycles=10)"
```

Notes:
- `max_cycles` exists for bounded host-side testing.
- On actual boards, `boot.py` calls `kernel.start()` and runs continuously.

### 2) Run on ESP32 (MicroPython)

1. Copy project files to board filesystem.
2. Ensure `boot.py` and `kernel.py` are at root.
3. Reset board.

The kernel will initialize HAL/services, launch `home`, and enter main loop.

## Configuration

Primary config file: `data/config.json`

Includes defaults such as:
- board profile
- watchdog timeout
- main loop sleep interval
- allowed state keys
- board pin mapping

### Recommended ESP32-S3 Settings

Development (safe REPL/debug workflow):
- `watchdog_enabled: false`
- `uart_enabled: false`

Production:
- set `watchdog_enabled: true`
- enable UART only if needed (`uart_enabled: true`)
- use a non-console UART (`uart_id: 1` or `2`, with explicit pins for your board)

### Logging Limits (Flash Safety)

Logs are capped and rotated to avoid consuming the whole flash:
- `log_max_file_bytes`: max size of `latest.log` before rotation (default `32768`)
- `log_backup_count`: number of rotated backups kept (default `2`)
- `log_buffer_entries`: in-memory recent entries (default `200`)

## Non-Goals (Current Pass)

- Production OTA flashing pipeline
- Full Wi-Fi/MQTT protocol implementations
- Hard real-time multicore balancing

## Next Suggested Steps

- Replace service placeholders with real `network` and MQTT clients
- Add Core 1 worker loop and IPC bridge for heavy tasks
- Expand HAL drivers (SSD1306/ILI9341/touch controllers)
- Add app package loading/unloading policy and health telemetry

---

If you want, I can also add a `LICENSE`, `.gitignore`, and a short `CONTRIBUTING.md` to make this GitHub-ready in one pass.
