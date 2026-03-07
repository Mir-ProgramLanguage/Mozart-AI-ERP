"""
通知API - 系统通知接口
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.services.notification_service import NotificationService
from app.core.deps import get_current_active_user
from app.models.user import User
from app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    NotificationCreate
)


router = APIRouter(prefix="/notifications", tags=["通知系统"])


@router.get("/", response_model=NotificationListResponse)
async def get_notifications(
    unread_only: bool = Query(False, description="是否只获取未读通知"),
    limit: int = Query(50, ge=1, le=200, description="限制数量"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取通知列表
    
    获取当前用户的通知列表
    """
    if not current_user.actor_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户未关联Actor"
        )
    
    notifications = NotificationService.get_user_notifications(
        db=db,
        actor_id=str(current_user.actor_id),
        unread_only=unread_only,
        limit=limit
    )
    
    unread_count = NotificationService.get_unread_count(
        db=db,
        actor_id=str(current_user.actor_id)
    )
    
    return NotificationListResponse(
        notifications=[NotificationResponse.from_orm(n) for n in notifications],
        unread_count=unread_count,
        total=len(notifications)
    )


@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取未读通知数量
    """
    if not current_user.actor_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户未关联Actor"
        )
    
    count = NotificationService.get_unread_count(
        db=db,
        actor_id=str(current_user.actor_id)
    )
    
    return {"unread_count": count}


@router.post("/{notification_id}/read")
async def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    标记通知为已读
    """
    if not current_user.actor_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户未关联Actor"
        )
    
    notification = NotificationService.mark_as_read(
        db=db,
        notification_id=notification_id,
        actor_id=str(current_user.actor_id)
    )
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在"
        )
    
    return {"message": "已标记为已读", "notification": notification.to_dict()}


@router.post("/mark-all-read")
async def mark_all_as_read(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    标记所有通知为已读
    """
    if not current_user.actor_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户未关联Actor"
        )
    
    count = NotificationService.mark_all_as_read(
        db=db,
        actor_id=str(current_user.actor_id)
    )
    
    return {"message": f"已标记{count}条通知为已读"}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    删除通知
    """
    if not current_user.actor_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户未关联Actor"
        )
    
    success = NotificationService.delete_notification(
        db=db,
        notification_id=notification_id,
        actor_id=str(current_user.actor_id)
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在"
        )
    
    return {"message": "通知已删除"}
