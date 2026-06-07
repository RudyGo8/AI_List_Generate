# -*- coding: utf-8 -*-
import logging
import os
import re
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import tomllib
from zoneinfo import ZoneInfo

import structlog


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOG_PATH = BACKEND_ROOT / "logs"
LOG_TIMEZONE = ZoneInfo("Asia/Shanghai")

_TS_RE = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
_LOGGING_CONFIGURED = False


def _shanghai_now() -> datetime:
    return datetime.now(LOG_TIMEZONE)


def _add_shanghai_timestamp(logger, method_name, event_dict):
    event_dict["timestamp"] = _shanghai_now().strftime("%Y-%m-%d %H:%M:%S")
    return event_dict


def _read_project_version(default: str = "0.1.0") -> str:
    pyproject_file = PROJECT_ROOT / "pyproject.toml"
    try:
        data = tomllib.loads(pyproject_file.read_text(encoding="utf-8"))
        return data.get("project", {}).get("version", default)
    except Exception:
        return default


APP_VERSION = os.getenv("APP_VERSION", _read_project_version())


def _load_env_file(env_path: Path):
    if not env_path.exists():
        return
    try:
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value
    except Exception:
        pass


def _resolve_log_path(raw_path: str | None = None) -> Path:
    path = Path(raw_path or str(DEFAULT_LOG_PATH))
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


_load_env_file(PROJECT_ROOT / ".env")

MYSQL_USERNAME = os.getenv("MYSQL_USERNAME")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

LOG_PATH = str(_resolve_log_path(os.getenv("LOG_PATH")))

REDIS_URL = os.getenv("REDIS_URL", "").strip()
CATEGORY_CACHE_TTL_SECONDS = int(os.getenv("CATEGORY_CACHE_TTL_SECONDS", "21600"))
EMBEDDING_CACHE_TTL_SECONDS = int(os.getenv("EMBEDDING_CACHE_TTL_SECONDS", "86400"))


class _StructlogFormatter(logging.Formatter):
    """structlog messages are preformatted; external logs get a prefix."""

    def format(self, record):
        record.exc_info = None
        record.exc_text = None
        msg = super().format(record)
        if not _TS_RE.match(_ANSI_RE.sub("", msg)):
            msg = f"{self.formatTime(record)} [{record.levelname:<8s}] {record.name}: {msg}"
        return msg


class StripAnsiFormatter(_StructlogFormatter):
    """File output should not contain ANSI color codes."""

    _ansi_re = re.compile(r"\x1b\[[0-9;]*m")

    def format(self, record):
        record.msg = self._ansi_re.sub("", str(record.msg))
        return super().format(record)


def setup_logging() -> None:
    global _LOGGING_CONFIGURED
    if _LOGGING_CONFIGURED:
        return

    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    env = os.getenv("ENV", "development").lower()
    log_dir = _resolve_log_path(os.getenv("LOG_PATH"))
    is_prod = env in ("production", "prod")

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        _add_shanghai_timestamp,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if is_prod:
        processors = shared_processors + [
            structlog.processors.JSONRenderer(ensure_ascii=False),
        ]
    else:
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(
                colors=True,
                pad_level=True,
                exception_formatter=structlog.dev.plain_traceback,
            ),
        ]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(log_level)

    console = logging.StreamHandler()
    console.setLevel(log_level)
    console.setFormatter(_StructlogFormatter("%(message)s"))
    root_logger.addHandler(console)

    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = TimedRotatingFileHandler(
            log_dir / "ai_list_backend.log",
            when="midnight",
            interval=1,
            backupCount=30,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(StripAnsiFormatter("%(message)s"))
        root_logger.addHandler(file_handler)
    except OSError:
        root_logger.warning("file_logging_unavailable log_dir=%s", str(log_dir))

    for ext in ("uvicorn", "uvicorn.error"):
        ext_logger = logging.getLogger(ext)
        ext_logger.handlers.clear()
        ext_logger.propagate = True
        ext_logger.setLevel(log_level)

    for name in ("httpx", "sqlalchemy.engine", "uvicorn.access"):
        logging.getLogger(name).setLevel(logging.WARNING)

    _log = structlog.get_logger(__name__)
    _log.info(
        "logging_initialized",
        log_level=log_level,
        env=env,
        log_dir=str(log_dir) if log_dir.exists() else None,
    )
    _LOGGING_CONFIGURED = True


def get_logger(name: str | None = None):
    return structlog.get_logger(name)


setup_logging()
logger = get_logger(__name__)


if __name__ == "__main__":
    logger.info("test_start")
    logger.info("with_params", request_id="test001", duration_ms=456)
    logger.warning("warning_test")
    logger.error("error_test")
    try:
        1 / 0
    except Exception:
        logger.exception("exception_test")
    logger.info("test_complete")
    print(LOG_PATH)
