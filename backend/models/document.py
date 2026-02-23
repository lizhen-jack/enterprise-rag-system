"""
文档模型
"""

from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class DocumentBase(SQLModel):
    """文档基础信息"""
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    file_type: str = Field(max_length=20)
    file_size: int  # 字节


class Document(DocumentBase, table=True):
    """文档表"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    file_path: str = Field(max_length=500)
    chunk_count: int = Field(default=0)
    status: str = Field(default="processing", max_length=20)  # processing/completed/failed
    indexed_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DocumentCreate(DocumentBase):
    """创建文档请求"""
    file_path: str


class DocumentPublic(DocumentBase):
    """公开文档信息"""
    id: int
    user_id: int
    chunk_count: int
    status: str
    indexed_at: Optional[datetime]
    created_at: datetime


class DocumentUpdate(SQLModel):
    """更新文档信息"""
    title: Optional[str] = None
    description: Optional[str] = None
