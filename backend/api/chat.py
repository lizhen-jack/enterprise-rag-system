"""
对话与检索API
RAG问答、长期记忆集成、上下文管理
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from core.database import get_db
from models.user import User
from models.conversation import Conversation, Message, ConversationCreate, ConversationPublic, MessagePublic, ChatRequest, ChatResponse
from api.users import get_current_user
from services.rag_service import RAGService, MemoryService

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """RAG对话（集成文档检索+长期记忆）"""
    from datetime import datetime

    rag_service = RAGService()
    memory_service = MemoryService(db)

    # 创建或获取对话
    conversation_id = request.conversation_id
    if conversation_id is None:
        # 创建新对话
        conversation = Conversation(
            user_id=current_user.id,
            title=request.message[:50] + "..."
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        conversation_id = conversation.id
    else:
        # 获取现有对话
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user.id
            )
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="对话不存在"
            )

    # 保存用户消息
    user_message = Message(
        conversation_id=conversation_id,
        user_id=current_user.id,
        content=request.message,
        message_type="user"
    )
    db.add(user_message)
    await db.commit()

    # 收集上下文
    context_parts = []

    # 1. 文档检索
    document_sources = []
    if request.use_rag:
        search_results = await rag_service.search(
            query=request.message,
            user_id=current_user.id,
            top_k=request.top_k
        )
        document_sources = search_results

        for result in search_results:
            context_parts.append(f"[文档: {result['document_title']}]\n{result['content']}\n")

    # 2. 长期记忆检索
    memory_sources = []
    if request.use_memory:
        memories = await memory_service.retrieve_memories(
            user_id=current_user.id,
            limit=3
        )
        memory_sources = [{"content": mem.content, "category": mem.category} for mem in memories]

        for memory in memories:
            context_parts.append(f"[记忆: {memory.category or '通用'}]\n{memory.content}\n")

    # 获取对话历史
    history_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(20)
    )
    history_messages = [
        {"role": "user" if m.message_type == "user" else "assistant", "content": m.content}
        for m in reversed(history_messages.scalars().all())
        if m.message_type in ["user", "assistant"]
    ]

    # 构建上下文
    context = "\n\n".join(context_parts) if context_parts else "暂无相关上下文信息。"

    # 生成AI回复
    try:
        reply = await rag_service.chat(
            query=request.message,
            context=context,
            conversation_history=history_messages,
            temperature=request.temperature
        )
    except Exception as e:
        print(f"AI回复生成失败: {e}")
        reply = f"抱歉，生成回复时出现错误：{str(e)}"

    # 保存AI消息
    assistant_message = Message(
        conversation_id=conversation_id,
        user_id=current_user.id,
        content=reply,
        message_type="assistant",
        retrieval_context=context[:2000]  # 截断过长上下文
    )
    db.add(assistant_message)

    # 更新对话信息
    conversation.message_count += 2
    conversation.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(assistant_message)

    return ChatResponse(
        message_id=assistant_message.id,
        conversation_id=conversation_id,
        reply=reply,
        sources=document_sources,
        memories=memory_sources
    )


@router.get("/conversations", response_model=List[ConversationPublic])
async def list_conversations(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取对话列表"""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
        .offset(skip)
        .limit(limit)
    )
    conversations = result.scalars().all()
    return conversations


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessagePublic])
async def get_messages(
    conversation_id: int,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取对话消息"""
    # 验证对话归属
    conv_result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    if not conv_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )

    # 获取消息
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .offset(skip)
        .limit(limit)
    )
    messages = result.scalars().all()
    return messages
