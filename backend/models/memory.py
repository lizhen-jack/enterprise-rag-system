"""
长期记忆模型
参考OpenClaw的记忆管理方法
"""

from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class MemoryBase(SQLModel):
    """记忆基础信息"""
    content: str = Field(max_length=2000)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)  # 重要性评分
    category: Optional[str] = Field(default=None, max_length=50)  # 分类
    tags: Optional[str] = Field(default=None, max_length=200)  # 标签，逗号分隔


class Memory(MemoryBase, table=True):
    """长期记忆表"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    # 记忆来源：手动添加/对话提取/系统生成
    source: str = Field(default="manual", max_length=20)
    # 访问统计
    access_count: int = Field(default=0)
    last_accessed: Optional[datetime] = Field(default=None)

    # 过期管理
    expires_at: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class MemoryCreate(MemoryBase):
    """创建记忆请求"""
    source: Optional[str] = "manual"



class MemoryPublic(MemoryBase):
    """公开记忆信息"""
    id: int
    user_id: int
    source: str
    access_count: int
    last_accessed: Optional[datetime]
    is_active: bool
    created_at: datetime


class MemoryUpdate(SQLModel):
    """更新记忆信息"""
    content: Optional[str] = None
    importance: Optional[float] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    is_active: Optional[bool] = None


class MemoryRetrieval(SQLModel):
    """记忆检索参数"""
    query: str
    category: Optional[str] = None
    min_importance: Optional[float] = 0.0
    limit: int = Field(default=5, ge=1, le=20)
