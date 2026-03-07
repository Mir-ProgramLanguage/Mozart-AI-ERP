"""
认证服务 - 用户注册、登录、令牌管理
"""

from typing import Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.contribution import Actor, ActorType
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token
)
from app.config import settings


class AuthService:
    """认证服务"""
    
    @staticmethod
    def create_user(
        db: Session,
        username: str,
        email: str,
        password: str,
        display_name: Optional[str] = None,
        is_superuser: bool = False
    ) -> Tuple[User, Actor]:
        """
        创建用户和关联的Actor
        
        Args:
            db: 数据库会话
            username: 用户名
            email: 邮箱
            password: 密码
            display_name: 显示名称
            is_superuser: 是否超级用户
        
        Returns:
            (用户对象, Actor对象)
        
        Raises:
            ValueError: 如果用户名或邮箱已存在
        """
        # 检查用户名是否存在
        if db.query(User).filter(User.username == username).first():
            raise ValueError("用户名已存在")
        
        # 检查邮箱是否存在
        if db.query(User).filter(User.email == email).first():
            raise ValueError("邮箱已存在")
        
        # 检查显示名称是否存在
        if not display_name:
            display_name = username
        
        if db.query(Actor).filter(Actor.display_name == display_name).first():
            raise ValueError("显示名称已存在")
        
        # 创建Actor
        actor = Actor(
            display_name=display_name,
            actor_type=ActorType.HUMAN,
            capabilities={},
            total_contributions=0,
            total_rewards=0,
            available_rewards=0,
            trust_score=0.5,
            reputation_score=0.5
        )
        db.add(actor)
        db.flush()  # 获取actor.id
        
        # 创建用户
        user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            actor_id=actor.id,
            is_superuser=is_superuser,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        db.refresh(actor)
        
        # 更新Actor的user_id
        actor.user_id = user.id
        db.commit()
        
        return user, actor
    
    @staticmethod
    def authenticate_user(
        db: Session,
        username: str,
        password: str
    ) -> Optional[User]:
        """
        认证用户
        
        Args:
            db: 数据库会话
            username: 用户名或邮箱
            password: 密码
        
        Returns:
            用户对象，如果认证失败则返回None
        """
        # 尝试通过用户名或邮箱查找用户
        user = db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        db.commit()
        
        return user
    
    @staticmethod
    def create_tokens(user: User) -> dict:
        """
        为用户创建令牌
        
        Args:
            user: 用户对象
        
        Returns:
            包含访问令牌和刷新令牌的字典
        """
        # 创建访问令牌
        access_token = create_access_token(
            subject=user.id,
            extra_data={
                "username": user.username,
                "is_superuser": user.is_superuser
            }
        )
        
        # 创建刷新令牌
        refresh_token = create_refresh_token(subject=user.id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    @staticmethod
    def refresh_access_token(
        db: Session,
        refresh_token: str
    ) -> Optional[dict]:
        """
        刷新访问令牌
        
        Args:
            db: 数据库会话
            refresh_token: 刷新令牌
        
        Returns:
            新的令牌字典，如果刷新失败则返回None
        """
        # 验证刷新令牌
        user_id = verify_token(refresh_token, token_type="refresh")
        
        if not user_id:
            return None
        
        # 获取用户
        user = db.query(User).filter(User.id == int(user_id)).first()
        
        if not user or not user.is_active:
            return None
        
        # 创建新令牌
        return AuthService.create_tokens(user)
    
    @staticmethod
    def change_password(
        db: Session,
        user: User,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        修改密码
        
        Args:
            db: 数据库会话
            user: 用户对象
            old_password: 旧密码
            new_password: 新密码
        
        Returns:
            是否成功
        """
        # 验证旧密码
        if not verify_password(old_password, user.hashed_password):
            return False
        
        # 更新密码
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        
        return True
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        根据ID获取用户
        
        Args:
            db: 数据库会话
            user_id: 用户ID
        
        Returns:
            用户对象
        """
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """
        根据用户名获取用户
        
        Args:
            db: 数据库会话
            username: 用户名
        
        Returns:
            用户对象
        """
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        根据邮箱获取用户
        
        Args:
            db: 数据库会话
            email: 邮箱
        
        Returns:
            用户对象
        """
        return db.query(User).filter(User.email == email).first()
