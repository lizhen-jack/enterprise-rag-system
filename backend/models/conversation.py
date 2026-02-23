"""
对话与消息模型
支持：对话历史、上下文管理
"""

from sqlalchemy import Column, JSON
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any


class ConversationBase(SQLModel):
    """对话基础信息"""
    title: str = Field(max_length=200)
    context_summary: Optional[str] = Field(default=None, max_length=1000)
    # 用户上下文元数据（存储JSON）
    context_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class Conversation(ConversationBase, table=True):
    """对话表"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    message_count: int = Field(default=0)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ConversationCreate(ConversationBase):
    """创建对话请求"""
    pass


class ConversationPublic(ConversationBase):
    """公开对话信息"""
    id: int
    user_id: int
    message_count: int
    is_active: bool
    created_at: datetime


class MessageBase(SQLModel):
    """消息基础信息"""
    content: str = Field(max_length=5000)
    # message_type: user/assistant/system
    message_type: str = Field(max_length=20)
    # 引用的文档块IDs（JSON数组）
    cited_chunks: Optional[List[int]] = Field(default=None)


class Message(MessageBase, table=True):
    """消息表"""
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)

    # RAG相关信息
    retrieval_context: Optional[str] = Field(default=None, max_length=2000)  # 检索到的上下文摘要

    created_at: datetime = Field(default_factory=datetime.utcnow)


class MessageCreate(MessageBase):
    """创建消息请求"""
    conversation_id: int


class MessagePublic(MessageBase):
    """公开消息信息"""
    id: int
    conversation_id: int
    user_id: int
    retrieval_context: Optional[str]
    created_at: datetime


class ChatRequest(SQLModel):
    """对话请求"""
    conversation_id: Optional[int] = None  # None表示创建新对话
    message: str = Field(min_length=1, max_length=2000)
    # RAG参数
    use_rag: bool = True
    use_memory: bool = True
    top_k: Optional[int] = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class ChatResponse(SQLModel):
    """对话响应"""
    message_id: int
    conversation_id: int
    reply: str
    # 检索到的文档来源
    sources: Optional[List[Dict[str, Any]]] = None
    # 检索到的长期记忆
    memories: Optional[List[Dict[str, Any]]] = None
