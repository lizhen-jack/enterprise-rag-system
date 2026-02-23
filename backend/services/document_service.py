"""
文档索引服务
文档解析、分块、向量化、存储
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import os
from datetime import datetime

from models.document import Document
from services.rag_service import RAGService
from core.config import settings


class DocumentService:
    """文档处理服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.rag_service = RAGService()

    async def index_document(self, document_id: int):
        """索引文档到向量数据库"""
        # 获取文档
        result = await self.db.execute(select(Document).where(Document.id == document_id))
        document = result.scalar_one_or_none()

        if not document:
            raise ValueError(f"文档 {document_id} 不存在")

        try:
            # 1. 解析文档
            text = await self._parse_document(document.file_path, document.file_type)

            # 2. 文本分块
            chunks = await self._chunk_text(text)

            # 3. 向量化并存储
            chunk_ids = []
            for i, chunk in enumerate(chunks):
                chunk_id = await self.rag_service.index_chunk(
                    text=chunk,
                    metadata={
                        "document_id": document_id,
                        "user_id": document.user_id,
                        "chunk_index": i,
                        "file_name": document.title
                    }
                )
                chunk_ids.append(chunk_id)

            # 4. 更新文档状态
            document.chunk_count = len(chunks)
            document.status = "completed"
            document.indexed_at = datetime.utcnow()
            await self.db.commit()

            print(f"✅ 文档索引完成: {document.title}, {len(chunks)} 个块")

        except Exception as e:
            print(f"❌ 文档索引失败: {e}")
            document.status = "failed"
            await self.db.commit()
            raise

    async def _parse_document(self, file_path: str, file_type: str) -> str:
        """解析文档文本"""
        if file_type == "pdf":
            from services.parsers import parse_pdf
            return await parse_pdf(file_path)
        elif file_type in ["doc", "docx"]:
            from services.parsers import parse_docx
            return await parse_docx(file_path)
        elif file_type in ["txt", "md"]:
            from services.parsers import parse_text
            return await parse_text(file_path)
        elif file_type in ["xls", "xlsx"]:
            from services.parsers import parse_excel
            return await parse_excel(file_path)
        else:
            raise ValueError(f"不支持的文件类型: {file_type}")

    async def _chunk_text(self, text: str) -> List[str]:
        """文本分块"""
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + settings.CHUNK_SIZE
            # 优先在段落或句子边界分割
            if end < text_length:
                # 尝试在句号、换行符处分割
                possible_ends = [
                    text.rfind("。", start, end),
                    text.rfind("！", start, end),
                    text.rfind("？", start, end),
                    text.rfind("\n", start, end),
                ]
                best_end = max(e for e in possible_ends if e > start)
                if best_end > start + settings.CHUNK_SIZE // 2:
                    end = best_end + 1

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - settings.CHUNK_OVERLAP

        return chunks
