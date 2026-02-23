"""
长期记忆API
手动添加、检索、管理记忆
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from core.database import get_db
from models.user import User
from models.memory import Memory, MemoryCreate, MemoryPublic, MemoryUpdate, MemoryRetrieval
from api.users import get_current_user
from services.rag_service import MemoryService

router = APIRouter()


@router.post("", response_model=MemoryPublic, status_code=status.HTTP_201_CREATED)
async def add_memory(
    memory_create: MemoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """添加长期记忆"""
    memory_service = MemoryService(db)

    memory = await memory_service.add_memory(
        user_id=current_user.id,
        content=memory_create.content,
        importance=memory_create.importance,
        category=memory_create.category,
        source=memory_create.source
    )

    return memory


@router.post("/retrieve", response_model=List[MemoryPublic])
async def retrieve_memories(
    retrieval: MemoryRetrieval,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """检索长期记忆"""
    memory_service = MemoryService(db)

    memories = await memory_service.retrieve_memories(
        user_id=current_user.id,
        query=retrieval.query if retrieval.query else None,
        category=retrieval.category,
        min_importance=retrieval.min_importance,
        limit=retrieval.limit
    )

    return memories


@router.get("", response_model=List[MemoryPublic])
async def list_memories(
    category: str = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取记忆列表"""
    memory_service = MemoryService(db)

    memories = await memory_service.retrieve_memories(
        user_id=current_user.id,
        category=category,
        limit=limit
    )

    return memories


@router.get("/{memory_id}", response_model=MemoryPublic)
async def get_memory(
    memory_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取记忆详情"""
    result = await db.execute(
        select(Memory).where(
            Memory.id == memory_id,
            Memory.user_id == current_user.id
        )
    )
    memory = result.scalar_one_or_none()

    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记忆不存在"
        )

    # 更新访问统计
    memory.access_count += 1
    await db.commit()

    return memory


@router.put("/{memory_id}", response_model=MemoryPublic)
async def update_memory(
    memory_id: int,
    memory_update: MemoryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新记忆"""
    result = await db.execute(
        select(Memory).where(
            Memory.id == memory_id,
            Memory.user_id == current_user.id
        )
    )
    memory = result.scalar_one_or_none()

    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记忆不存在"
        )

    for field, value in memory_update.dict(exclude_unset=True).items():
        if value is not None:
            setattr(memory, field, value)

    await db.commit()
    await db.refresh(memory)

    return memory


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(
    memory_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除记忆（软删除）"""
    result = await db.execute(
        select(Memory).where(
            Memory.id == memory_id,
            Memory.user_id == current_user.id
        )
    )
    memory = result.scalar_one_or_none()

    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记忆不存在"
        )

    # 软删除
    memory.is_active = False
    await db.commit()

    return None


@router.post("/cleanup")
async def cleanup_expired(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """清理过期记忆"""
    memory_service = MemoryService(db)

    count = await memory_service.cleanup_expired_memories(user_id=current_user.id)

    return {"message": f"已清理 {count} 条过期记忆"}
