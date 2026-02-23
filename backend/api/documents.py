"""
文档管理API
上传、删除、查询文档
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import os
import uuid

from core.database import get_db
from core.security import get_current_user
from models.user import User
from services.document_service import DocumentService
from services.rag_service import RAGService
from core.config import settings

router = APIRouter()


def get_document_service(db: AsyncSession = Depends(get_db)) -> DocumentService:
    """获取DocumentService实例"""
    rag_service = RAGService(db)
    return DocumentService(db, rag_service)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """上传文档"""
    # 验证文件类型
    ext = os.path.splitext(file.filename)[1].lower()[1:]
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持此文件类型。支持的格式: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # 验证文件大小
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件大小超过限制（最大 {settings.MAX_FILE_SIZE // (1024*1024)}MB）"
        )

    # 保存文件
    upload_dir = settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)

    # 生成唯一文件名
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(upload_dir, unique_filename)

    async with open(file_path, "wb") as f:
        f.write(content)

    # 创建文档记录并处理
    doc_service = get_document_service(db)
    document = await doc_service.upload_document(
        user_id=current_user.id,
        file_path=file_path,
        filename=file.filename,
        file_size=len(content),
        mime_type=file.content_type or "application/octet-stream"
    )

    return {
        "id": document.id,
        "filename": document.filename,
        "status": document.status,
        "chunk_count": document.chunk_count,
        "total_chars": document.total_chars,
        "created_at": document.created_at.isoformat()
    }


@router.get("")
async def list_documents(
    status: str = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取文档列表"""
    doc_service = get_document_service(db)
    documents = await doc_service.get_user_documents(current_user.id, status, limit)

    return {
        "documents": [
            {
                "id": doc.id,
                "filename": doc.filename,
                "status": doc.status,
                "chunk_count": doc.chunk_count,
                "total_chars": doc.total_chars,
                "created_at": doc.created_at.isoformat(),
                "processed_at": doc.processed_at.isoformat() if doc.processed_at else None,
                "error_message": doc.error_message
            }
            for doc in documents
        ]
    }


@router.get("/stats")
async def get_document_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取文档统计"""
    doc_service = get_document_service(db)
    stats = await doc_service.get_document_stats(current_user.id)

    return stats


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除文档"""
    doc_service = get_document_service(db)
    success = await doc_service.delete_document(document_id, current_user.id)

    if not success:
        raise HTTPException(status_code=404, detail="文档不存在或无权限")

    return {"message": "文档删除成功"}
