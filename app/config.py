'''
@create_time: 2026/3/25 下午8:17
@Author: GeChao
@File: config.py
'''
import logging
from logging.handlers import TimedRotatingFileHandler

# 数据库配置
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USERNAME = "root"
MYSQL_PASSWORD = "your_password"
MYSQL_DATABASE = "ecommerce_ai"

# 日志配置
# 日志配置
LOG_PATH = './logs'
def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 控制台输出
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 文件输出(按天轮转)
    file_handler = TimedRotatingFileHandler(
        f'{LOG_PATH}/app.log',
        when='midnight',
        backupCount=7
    )
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

setup_logging()
logger = logging.getLogger()

