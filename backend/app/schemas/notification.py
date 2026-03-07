"""
通知相关的Schema
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class NotificationResponse(BaseModel):
    """通知响应Schema"""
    id: int
    recipient_id: str
    notification_type: str
    title: str
    message: str
    related_object_type: Optional[str] = None
    related_object_id: Optional[str] = None
    is_read: bool = False
    read_at: Optional[datetime] = None
    priority: int = 3
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """通知列表响应Schema"""
    notifications: list[NotificationResponse]
    unread_count: int
    total: int


class NotificationCreate(BaseModel):
    """创建通知Schema（管理员使用）"""
    recipient_id: str = Field(..., description="接收者ID")
    notification_type: str = Field(..., description="通知类型")
    title: str = Field(..., max_length=200, description="通知标题")
    message: str = Field(..., description="通知消息")
    related_object_type: Optional[str] = Field(None, description="关联对象类型")
    related_object_id: Optional[str] = Field(None, description="关联对象ID")
    priority: int = Field(3, ge=1, le=5, description="优先级（1-5）")
