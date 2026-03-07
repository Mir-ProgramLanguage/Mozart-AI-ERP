"""
数据库初始化脚本

用于开发和测试环境，创建所有表
"""

from app.database import engine, Base
from app.models.contribution import Actor, Event, Reward, Task, ActorInteraction
from app.models.user import User, Token
from app.models.notification import Notification


def init_db():
    """创建所有表"""
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")


if __name__ == "__main__":
    init_db()
