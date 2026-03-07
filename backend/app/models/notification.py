"""
通知模型 - 用于系统通知和消息推送
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from app.database import Base


class NotificationType:
    """通知类型常量"""
    TASK_ASSIGNED = "task_assigned"          # 任务分配
    TASK_COMPLETED = "task_completed"        # 任务完成
    TASK_VERIFIED = "task_verified"          # 任务验证
    CONTRIBUTION_SUBMITTED = "contribution_submitted"  # 贡献提交
    CONTRIBUTION_VERIFIED = "contribution_verified"    # 贡献验证
    REWARD_GRANTED = "reward_granted"        # 回报发放
    SYSTEM = "system"                        # 系统通知


class Notification(Base):
    """
    通知模型
    
    用于记录和推送系统通知
    """
    
    __tablename__ = "notifications"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 接收者（Actor ID）
    recipient_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # 通知类型
    notification_type = Column(String(50), nullable=False, index=True)
    
    # 通知内容
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # 关联对象（可选）
    related_object_type = Column(String(50), nullable=True)  # task, contribution, reward
    related_object_id = Column(String(100), nullable=True)
    
    # 通知状态
    is_read = Column(Boolean, default=False, index=True)
    read_at = Column(DateTime, nullable=True)
    
    # 优先级（1-5，5最高）
    priority = Column(Integer, default=3)
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "recipient_id": str(self.recipient_id),
            "notification_type": self.notification_type,
            "title": self.title,
            "message": self.message,
            "related_object_type": self.related_object_type,
            "related_object_id": self.related_object_id,
            "is_read": self.is_read,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "priority": self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
