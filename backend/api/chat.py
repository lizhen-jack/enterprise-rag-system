"""
对话和RAG API
智能问答、语义检索、长期记忆
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional

from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.conversation import Conversation, Message
from services.rag_service import RAGService, MemoryService
from sqlalchemy import select

router = APIRouter()


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str
    conversation_id: Optional[int] = None
    document_ids: Optional[List[int]] = None
    user_prompt: str = ""
    temperature: float = 0.7


class ChatResponse(BaseModel):
    """聊天响应"""
    message_id: int
    conversation_id: int
    response: str
    sources: List[dict]
    created_at: str


class MemoryRequest(BaseModel):
    """添加记忆请求"""
    content: str
    importance: float = 0.5
    category: str = None
    tags: List[str] = None


def get_rag_service(db: AsyncSession = Depends(get_db)) -> RAGService:
    """获取RAGService实例"""
    return RAGService(db)


def get_memory_service(db: AsyncSession = Depends(get_db)) -> MemoryService:
    """获取MemoryService实例"""
    return MemoryService(db)


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """智能对话（RAG）"""
    rag_service = get_rag_service(db)

    # 获取或创建对话
    if request.conversation_id:
        query = select(Conversation).where(
            Conversation.id == request.conversation_id,
            Conversation.user_id == current_user.id
        )
        result = await db.execute(query)
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise HTTPException(status_code=404, detail="对话不存在")
    else:
        # 创建新对话
        conversation = Conversation(
            user_id=current_user.id,
            title=request.message[:50] + "..."
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

    # 获取对话历史
    history_query = select(Message).where(
        Message.conversation_id == conversation.id
    ).order_by(Message.created_at)
    history_result = await db.execute(history_query)
    messages = history_result.scalars().all()

    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in messages[-20:]  # 最近20条
    ]

    # RAG生成回复
    result = await rag_service.chat(
        query=request.message,
        user_id=current_user.id,
        conversation_history=conversation_history,
        user_prompt=request.user_prompt,
        document_ids=request.document_ids,
        temperature=request.temperature
    )

    # 保存用户消息
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    await db.commit()

    # 保存AI回复
    ai_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=result["response"],
        sources=result.get("sources", [])
    )
    db.add(ai_message)
    await db.commit()
    await db.refresh(ai_message)

    return ChatResponse(
        message_id=ai_message.id,
        conversation_id=conversation.id,
        response=result["response"],
        sources=result.get("sources", []),
        created_at=ai_message.created_at.isoformat()
    )


@router.get("/conversations")
async def list_conversations(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取对话列表"""
    query = select(Conversation).where(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.updated_at.desc()).limit(limit)

    result = await db.execute(query)
    conversations = result.scalars().all()

    return {
        "conversations": [
            {
                "id": conv.id,
                "title": conv.title,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat()
            }
            for conv in conversations
        ]
    }


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取对话消息"""
    # 验证权限
    query = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    )
    result = await db.execute(query)
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")

    # 获取消息
    messages_query = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at)

    messages_result = await db.execute(messages_query)
    messages = messages_result.scalars().all()

    return {
        "conversation_id": conversation_id,
        "title": conversation.title,
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "sources": msg.sources,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]
    }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除对话"""
    # 验证权限
    query = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    )
    result = await db.execute(query)
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")

    # 删除消息
    await db.execute(
        select(Message).where(Message.conversation_id == conversation_id)
    )

    # 删除对话
    await db.delete(conversation)
    await db.commit()

    return {"message": "对话删除成功"}


@router.post("/memory")
async def add_memory(
    request: MemoryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """添加长期记忆"""
    memory_service = get_memory_service(db)

    memory = await memory_service.add_memory(
        user_id=current_user.id,
        content=request.content,
        importance=request.importance,
        category=request.category,
        tags=request.tags
    )

    return memory


@router.get("/memory")
async def get_memories(
    query: str = None,
    category: str = None,
    min_importance: float = 0.7,
    limit: int = 5,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """检索长期记忆"""
    memory_service = get_memory_service(db)

    memories = await memory_service.retrieve_memories(
        user_id=current_user.id,
        query=query,
        category=category,
        min_importance=min_importance,
        limit=limit
    )

    return {"memories": memories}


@router.delete("/memory/{memory_id}")
async def delete_memory(
    memory_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除长期记忆"""
    from models.memory import Memory

    query = select(Memory).where(
        Memory.id == memory_id,
        Memory.user_id == current_user.id
    )
    result = await db.execute(query)
    memory = result.scalar_one_or_none()

    if not memory:
        raise HTTPException(status_code=404, detail="记忆不存在")

    await db.delete(memory)
    await db.commit()

    return {"message": "记忆删除成功"}
