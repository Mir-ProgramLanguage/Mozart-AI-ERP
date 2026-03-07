"""
通知服务 - 创建和管理系统通知
"""

from typing import List, Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.notification import Notification, NotificationType
from app.models.contribution import Actor


class NotificationService:
    """通知服务"""
    
    @staticmethod
    def _to_uuid(value: str) -> UUID:
        """将字符串转换为UUID"""
        if isinstance(value, UUID):
            return value
        return UUID(value)
    
    @staticmethod
    def create_notification(
        db: Session,
        recipient_id: str,
        notification_type: str,
        title: str,
        message: str,
        related_object_type: Optional[str] = None,
        related_object_id: Optional[str] = None,
        priority: int = 3
    ) -> Notification:
        """
        创建通知
        
        Args:
            db: 数据库会话
            recipient_id: 接收者ID
            notification_type: 通知类型
            title: 通知标题
            message: 通知消息
            related_object_type: 关联对象类型
            related_object_id: 关联对象ID
            priority: 优先级
        
        Returns:
            通知对象
        """
        notification = Notification(
            recipient_id=NotificationService._to_uuid(recipient_id),
            notification_type=notification_type,
            title=title,
            message=message,
            related_object_type=related_object_type,
            related_object_id=related_object_id,
            priority=priority,
            is_read=False
        )
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        return notification
    
    @staticmethod
    def notify_task_assigned(
        db: Session,
        actor_id: str,
        task_id: str,
        task_title: str
    ) -> Notification:
        """通知任务分配"""
        return NotificationService.create_notification(
            db=db,
            recipient_id=actor_id,
            notification_type=NotificationType.TASK_ASSIGNED,
            title="新任务分配",
            message=f"您有新的任务：{task_title}",
            related_object_type="task",
            related_object_id=task_id,
            priority=4
        )
    
    @staticmethod
    def notify_contribution_verified(
        db: Session,
        actor_id: str,
        contribution_id: str,
        contribution_value: float
    ) -> Notification:
        """通知贡献验证"""
        return NotificationService.create_notification(
            db=db,
            recipient_id=actor_id,
            notification_type=NotificationType.CONTRIBUTION_VERIFIED,
            title="贡献已验证",
            message=f"您的贡献已验证通过，贡献值：{contribution_value:.2f}",
            related_object_type="contribution",
            related_object_id=contribution_id,
            priority=3
        )
    
    @staticmethod
    def notify_reward_granted(
        db: Session,
        actor_id: str,
        reward_id: str,
        reward_amount: float,
        reward_type: str
    ) -> Notification:
        """通知回报发放"""
        return NotificationService.create_notification(
            db=db,
            recipient_id=actor_id,
            notification_type=NotificationType.REWARD_GRANTED,
            title="回报发放",
            message=f"您获得了{reward_type}回报：{reward_amount:.2f}元",
            related_object_type="reward",
            related_object_id=reward_id,
            priority=4
        )
    
    @staticmethod
    def get_user_notifications(
        db: Session,
        actor_id: str,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Notification]:
        """
        获取用户通知列表
        
        Args:
            db: 数据库会话
            actor_id: 用户Actor ID
            unread_only: 是否只获取未读通知
            limit: 限制数量
        
        Returns:
            通知列表
        """
        query = db.query(Notification).filter(
            Notification.recipient_id == NotificationService._to_uuid(actor_id)
        )
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        return query.order_by(
            Notification.priority.desc(),
            Notification.created_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def mark_as_read(
        db: Session,
        notification_id: int,
        actor_id: str
    ) -> Optional[Notification]:
        """
        标记通知为已读
        
        Args:
            db: 数据库会话
            notification_id: 通知ID
            actor_id: 用户Actor ID
        
        Returns:
            通知对象，如果不存在则返回None
        """
        notification = db.query(Notification).filter(
            and_(
                Notification.id == notification_id,
                Notification.recipient_id == NotificationService._to_uuid(actor_id)
            )
        ).first()
        
        if notification and not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            db.commit()
            db.refresh(notification)
        
        return notification
    
    @staticmethod
    def mark_all_as_read(
        db: Session,
        actor_id: str
    ) -> int:
        """
        标记所有通知为已读
        
        Args:
            db: 数据库会话
            actor_id: 用户Actor ID
        
        Returns:
            更新的通知数量
        """
        now = datetime.utcnow()
        
        result = db.query(Notification).filter(
            and_(
                Notification.recipient_id == NotificationService._to_uuid(actor_id),
                Notification.is_read == False
            )
        ).update({
            "is_read": True,
            "read_at": now
        })
        
        db.commit()
        
        return result
    
    @staticmethod
    def get_unread_count(
        db: Session,
        actor_id: str
    ) -> int:
        """
        获取未读通知数量
        
        Args:
            db: 数据库会话
            actor_id: 用户Actor ID
        
        Returns:
            未读通知数量
        """
        return db.query(Notification).filter(
            and_(
                Notification.recipient_id == NotificationService._to_uuid(actor_id),
                Notification.is_read == False
            )
        ).count()
    
    @staticmethod
    def delete_notification(
        db: Session,
        notification_id: int,
        actor_id: str
    ) -> bool:
        """
        删除通知
        
        Args:
            db: 数据库会话
            notification_id: 通知ID
            actor_id: 用户Actor ID
        
        Returns:
            是否删除成功
        """
        notification = db.query(Notification).filter(
            and_(
                Notification.id == notification_id,
                Notification.recipient_id == NotificationService._to_uuid(actor_id)
            )
        ).first()
        
        if notification:
            db.delete(notification)
            db.commit()
            return True
        
        return False
