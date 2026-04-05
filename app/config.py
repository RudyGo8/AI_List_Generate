'''
@create_time: 2026/3/25 下午8:17
@Author: GeChao
@File: config.py
'''
import json
import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

# MySQL settings
MYSQL_USERNAME = os.getenv("MYSQL_USERNAME", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "123456")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "ai_list")

# Logging path
LOG_PATH = os.getenv("LOG_PATH", "./logs")


def json_formatter(record):
    """Convert a logging record to a JSON string."""
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
    """Custom formatter to output logs in JSON format."""

    def format(self, record):
        record.asctime = self.formatTime(record)
        return json_formatter(record)


def setup_logging(log_file_path=None):
    """Set up logging for the application."""
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

    print("日志已写入 test_log.log")
