'''
@create_time: 2026/3/25 涓嬪崍8:17
@Author: GeChao
@File: config.py
'''
import json
import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


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


PROJECT_ROOT = Path(__file__).resolve().parents[1]
# 切换docker环境
for env_candidate in (
    # PROJECT_ROOT / ".env.compose",
    PROJECT_ROOT / ".env",
    # PROJECT_ROOT.parent / ".env.compose",
    PROJECT_ROOT.parent / ".env",
):
    _load_env_file(env_candidate)

MYSQL_USERNAME = os.getenv("MYSQL_USERNAME")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

LOG_PATH = os.getenv("LOG_PATH", "./logs")

REDIS_URL = os.getenv("REDIS_URL", "").strip()
CATEGORY_CACHE_TTL_SECONDS = int(os.getenv("CATEGORY_CACHE_TTL_SECONDS", "21600"))
EMBEDDING_CACHE_TTL_SECONDS = int(os.getenv("EMBEDDING_CACHE_TTL_SECONDS", "86400"))


def json_formatter(record):
    log_record = {
        "time": record.asctime,
        "name": record.name,
        "level": record.levelname,
        "message": record.getMessage(),
        "filename": record.filename,
        "funcName": record.funcName,
        "lineno": record.lineno
    }
    return json.dumps(log_record, ensure_ascii=False)


class JsonLogFormatter(logging.Formatter):

    def format(self, record):
        record.asctime = self.formatTime(record)
        return json_formatter(record)


def setup_logging(log_file_path=None):
    root_logger = logging.getLogger()
    if getattr(root_logger, "_ai_list_logging_configured", False):
        return

    os.makedirs(LOG_PATH, exist_ok=True)

    if log_file_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file_path = f"{LOG_PATH}/ai_image_api_{timestamp}.log"

    root_logger.setLevel(logging.INFO)

    json_log_formatter = JsonLogFormatter()

    file_handler = TimedRotatingFileHandler(log_file_path, when='midnight', interval=1, backupCount=5)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(json_log_formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(json_log_formatter)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)
    root_logger._ai_list_logging_configured = True


setup_logging()
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    setup_logging("test_log.log")
    test_logger = logging.getLogger(__name__)

    test_logger.info("This is a test log message.")
    test_logger.error("This is an error log message.")

    print("鏃ュ織宸插啓鍏?test_log.log")

