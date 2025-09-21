import json, logging, os, sys, time

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base = {
            "ts": time.time(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            base["exc"] = self.formatException(record.exc_info)
        return json.dumps(base, separators=(",", ":"))

def _level_from_env(default=logging.INFO) -> int:
    name = os.getenv("AIOSCORE_LOG_LEVEL", "").upper()
    return {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARN": logging.WARN,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }.get(name, default)

def setup(level: int | None = None) -> None:
    """Structured JSON logs to stdout; idempotent."""
    lvl = _level_from_env(level or logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    # Replace any existing handlers so we don’t double-log
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(lvl)
