"""
文档管理API
文档上传、索引、查询、删除
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import os

from core.database import get_db
from core.config import settings
from models.user import User
from models.document import Document, DocumentCreate, DocumentPublic, DocumentUpdate
from api.users import get_current_user
from services.document_service import DocumentService

router = APIRouter()


@router.post("/upload", response_model=DocumentPublic, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: str = None,
    description: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """上传文档并启动索引处理"""
    # 验证文件类型
    file_ext = file.filename.split('.')[-1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型，允许的类型: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # 验证文件大小
    file_size = 0
    content = await file.read()
    file_size = len(content)

    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制（最大 {settings.MAX_FILE_SIZE // (1024*1024)}MB）"
        )

    # 保存文件
    user_upload_dir = os.path.join(settings.UPLOAD_DIR, str(current_user.id))
    os.makedirs(user_upload_dir, exist_ok=True)

    file_path = os.path.join(user_upload_dir, f"{file.filename}")

    with open(file_path, "wb") as f:
        f.write(content)

    # 创建文档记录
    document = Document(
        user_id=current_user.id,
        title=title or file.filename,
        description=description,
        file_type=file_ext,
        file_size=file_size,
        file_path=file_path,
        status="processing"
    )

    db.add(document)
    await db.commit()
    await db.refresh(document)

    # 异步启动文档索引（后台任务）
    # 使用Celery或简单异步任务
    try:
        doc_service = DocumentService(db)
        await doc_service.index_document(document.id)
    except Exception as e:
        print(f"文档索引失败: {e}")
        document.status = "failed"
        await db.commit()

    return document


@router.get("", response_model=List[DocumentPublic])
async def list_documents(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户的文档列表"""
    result = await db.execute(
        select(Document)
        .where(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    documents = result.scalars().all()
    return documents


@router.get("/{document_id}", response_model=DocumentPublic)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取文档详情"""
    result = await db.execute(
        select(Document)
        .where(Document.id == document_id, Document.user_id == current_user.id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    return document


@router.put("/{document_id}", response_model=DocumentPublic)
async def update_document(
    document_id: int,
    document_update: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新文档信息"""
    result = await db.execute(
        select(Document)
        .where(Document.id == document_id, Document.user_id == current_user.id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    for field, value in document_update.dict(exclude_unset=True).items():
        if value is not None:
            setattr(document, field, value)

    await db.commit()
    await db.refresh(document)

    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除文档"""
    result = await db.execute(
        select(Document)
        .where(Document.id == document_id, Document.user_id == current_user.id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    # 删除文件
    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    # 从数据库删除
    await db.delete(document)
    await db.commit()

    # 删除向量数据（待实现）
    # await delete_from_vector_db(document_id)

    return None
