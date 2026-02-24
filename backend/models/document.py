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
    filename: str = Field(max_length=255)
    file_hash: str = Field(default="", max_length=64)
    mime_type: str = Field(default="application/octet-stream", max_length=100)
    total_chars: int = Field(default=0)
    error_message: Optional[str] = Field(default=None, max_length=1000)


class Document(DocumentBase, table=True):
    """文档表"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    filename: str = Field(max_length=255)  # 原始文件名
    file_path: str = Field(max_length=500)
    file_hash: str = Field(default="", max_length=64)  # SHA256哈希，用于去重
    mime_type: str = Field(default="application/octet-stream", max_length=100)
    total_chars: int = Field(default=0)  # 字符总数
    chunk_count: int = Field(default=0)  # 分块数量
    status: str = Field(default="processing", max_length=20)  # processing/completed/failed
    processed_at: Optional[datetime] = Field(default=None)
    error_message: Optional[str] = Field(default=None, max_length=1000)
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
