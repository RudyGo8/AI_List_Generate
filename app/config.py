'''
@create_time: 2026/3/25 下午8:17
@Author: GeChao
@File: config.py
'''
import json
import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

# mysql 配置
MYSQL_USERNAME = "root"
MYSQL_PASSWORD = "123456"
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_DATABASE = "ai_list"

# 日志路径
LOG_PATH = './logs'


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
    # 将 ensure_ascii 设置为 False
    return json.dumps(log_record, ensure_ascii=False)


class JsonLogFormatter(logging.Formatter):
    """Custom formatter to output logs in JSON format."""

    def format(self, record):
        record.asctime = self.formatTime(record)
        return json_formatter(record)


def setup_logging(log_file_path=None):
    """Set up logging for the application."""
    if log_file_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file_path = "%s/ai_image_api_%s.log" % (LOG_PATH, timestamp)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create a JSON formatter
    json_formatter = JsonLogFormatter()

    # File handler to write logs to a file daily
    file_handler = TimedRotatingFileHandler(log_file_path, when='midnight', interval=1, backupCount=5)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(json_formatter)

    # Stream handler to write logs to the console
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(json_formatter)

    # Add handlers to the root logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


setup_logging()
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger = setup_logging("test_log.log")
    test_logger = logging.getLogger(__name__)

    test_logger.info("This is a test log message.")
    test_logger.error("This is an error log message.")

    print("日志已写入test_log.log")

