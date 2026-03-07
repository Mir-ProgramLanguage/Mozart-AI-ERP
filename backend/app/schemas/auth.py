"""
认证相关的Schema
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, Any
from datetime import datetime
from uuid import UUID


class UserCreate(BaseModel):
    """用户注册Schema"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    display_name: Optional[str] = Field(None, max_length=50, description="显示名称")


class UserLogin(BaseModel):
    """用户登录Schema"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


class UserResponse(BaseModel):
    """用户响应Schema"""
    id: int
    username: str
    email: str
    actor_id: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    @field_validator('actor_id', mode='before')
    @classmethod
    def uuid_to_str(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        if isinstance(v, UUID):
            return str(v)
        return v
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """令牌响应Schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求Schema"""
    refresh_token: str


class PasswordChange(BaseModel):
    """修改密码Schema"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")


class PasswordReset(BaseModel):
    """重置密码Schema"""
    email: EmailStr = Field(..., description="邮箱")


class ActorCreate(BaseModel):
    """创建Actor Schema（注册时使用）"""
    display_name: str = Field(..., max_length=50, description="显示名称")
    capabilities: Optional[dict] = Field(default={}, description="能力图谱")
