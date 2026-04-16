'''
@create_time: 2025/6/21 下午8:21
@Author: GeChao
@File: database.py
'''

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.app.config import MYSQL_HOST, MYSQL_PORT, MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_DATABASE

import pymysql

pymysql.install_as_MySQLdb()
# 构建数据库连接URL
SQLALCHEMY_DATABASE_URL = f"mysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"

# 连接池
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,
    pool_size=30,
    pool_recycle=3600,
    max_overflow=50,
    pool_timeout=60,
    pool_pre_ping=True
)

sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db_instance():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()
