"""
用户模型
"""

from sqlalchemy import Column, String, DateTime
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class UserBase(SQLModel):
    """用户基础信息"""
    username: str = Field(index=True, unique=True, max_length=50)
    email: str = Field(index=True, unique=True, max_length=100)
    full_name: Optional[str] = Field(default=None, max_length=100)


class User(UserBase, table=True):
    """用户表"""
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field(max_length=255)
    avatar_url: Optional[str] = Field(default=None)
    company: Optional[str] = Field(default=None, max_length=100)
    department: Optional[str] = Field(default=None, max_length=100)
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserCreate(UserBase):
    """创建用户请求"""
    password: str = Field(min_length=6, max_length=100)


class UserUpdate(SQLModel):
    """更新用户信息"""
    email: Optional[str] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    company: Optional[str] = None
    department: Optional[str] = None


class UserPublic(UserBase):
    """公开用户信息（不含密码）"""
    id: int
    avatar_url: Optional[str]
    company: Optional[str]
    department: Optional[str]
    created_at: datetime


class UserLogin(SQLModel):
    """用户登录"""
    username: str
    password: str


class Token(SQLModel):
    """JWT Token"""
    access_token: str
    token_type: str = "bearer"


class TokenData(SQLModel):
    """Token数据"""
    username: Optional[str] = None
