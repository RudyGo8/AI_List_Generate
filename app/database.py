'''
@create_time: 2025/6/21 下午8:21
@Author: GeChao
@File: database.py
'''

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import MYSQL_HOST, MYSQL_PORT, MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_DATABASE

# 构建数据库连接URL
SQLALCHEMY_DATABASE_URL = f"mysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"

# 创建引擎(连接池)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,  # 数据库连接URL
    echo=False,
    pool_size=10,
    pool_recycle=3600,
    pool_pre_ping=True
)

# 创建Session工厂
session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建Base类
Base = declarative_base()


# 获取数据库Session的函数
def get_db():
    db = session_factory()
    try:
        yield db
    finally:
        db.close()
