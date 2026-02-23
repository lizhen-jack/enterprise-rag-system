"""
RAG核心服务
向量检索、上下文构建、长期记忆集成
"""

from typing import List, Dict, Any, Optional
from pymilvus import connections, Collection
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

from core.config import settings


class RAGService:
    """RAG检索增强生成服务"""

    def __init__(self):
        # 初始化Milvus连接
        connections.connect(
            alias="default",
            host=settings.MILVUS_HOST,
            port=settings.MILVUS_PORT
        )
        self.collection = Collection(settings.MILVUS_COLLECTION)

        # 初始化Embedding模型（使用国内API）
        self.embeddings = OpenAIEmbeddings(
            openai_api_base=settings.AI_API_BASE,
            openai_api_key=settings.AI_API_KEY,
            model=settings.EMBEDDING_MODEL
        )

        # 初始化聊天模型
        self.llm = ChatOpenAI(
            openai_api_base=settings.AI_API_BASE,
            openai_api_key=settings.AI_API_KEY,
            model=settings.CHAT_MODEL,
            temperature=0.7
        )

    async def index_chunk(self, text: str, metadata: Dict[str, Any]) -> int:
        """索引文本块到向量数据库"""
        # 生成向量
        embedding = self.embeddings.embed_query(text)

        # 插入Milvus
        chunk_id = int(hash(text + str(metadata)) % (10 ** 9))  # 简化ID生成

        data = [
            [chunk_id],
            [metadata["user_id"]],
            [metadata["document_id"]],
            [embedding],
            [text],
            [metadata["file_name"]]
        ]

        # 这里需要实现Milvus插入逻辑
        # insert(...)
        # self.collection.flush()

        return chunk_id

    async def search(
        self,
        query: str,
        user_id: int,
        top_k: int = None,
        document_ids: List[int] = None
    ) -> List[Dict[str, Any]]:
        """语义检索"""
        top_k = top_k or settings.TOP_K

        # 生成查询向量
        query_embedding = self.embeddings.embed_query(query)

        # 在Milvus中搜索
        # results = search_vectors(query_embedding, user_id, top_k, document_ids)

        # 模拟返回结构
        return [
            {
                "chunk_id": 1,
                "document_id": 1,
                "document_title": "示例文档.pdf",
                "content": "检索到的内容块",
                "score": 0.95
            }
        ]

    async def chat(
        self,
        query: str,
        context: str,
        conversation_history: List[Dict],
        temperature: float = 0.7
    ) -> str:
        """生成对话回复"""
        # 构建提示模板
        template = """
你是一个专业的企业知识助手。根据提供的上下文和对话历史，回答用户的问题。

**上下文信息：**
{context}

**对话历史：**
{history}

**用户问题：**
{question}

**回答要求：**
1. 基于上下文信息回答，如果上下文中没有相关信息，请明确说明
2. 回答要准确、简洁、专业
3. 引用具体来源（文档标题）
4. 保持与上下文的一致性

回答：
"""

        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "history", "question"]
        )

        # 格式化对话历史
        history_text = ""
        for msg in conversation_history[-10:]:  # 只取最近10轮
            role = "用户" if msg["role"] == "user" else "助手"
            history_text += f"{role}: {msg['content']}\n"

        # 生成回复
        response = self.llm.predict(
            prompt.format(
                context=context,
                history=history_text,
                question=query
            )
        )

        return response


class MemoryService:
    """长期记忆服务（参考OpenClaw的记忆方法）"""

    def __init__(self, db):
        self.db = db

    async def add_memory(
        self,
        user_id: int,
        content: str,
        importance: float = 0.5,
        category: str = None,
        source: str = "manual"
    ):
        """添加长期记忆"""
        from models.memory import Memory

        memory = Memory(
            user_id=user_id,
            content=content,
            importance=importance,
            category=category,
            source=source,
            expires_at=self._calculate_expiry(importance)
        )

        self.db.add(memory)
        await self.db.commit()

        return memory

    async def retrieve_memories(
        self,
        user_id: int,
        query: Optional[str] = None,
        category: Optional[str] = None,
        min_importance: float = 0.0,
        limit: int = 5
    ) -> List[Memory]:
        """检索长期记忆"""
        from sqlalchemy import select
        from models.memory import Memory

        query_builder = select(Memory).where(
            Memory.user_id == user_id,
            Memory.is_active == True,
            Memory.importance >= min_importance
        )

        if category:
            query_builder = query_builder.where(Memory.category == category)

        # 如果有query，可以使用语义检索（这里用简单包含）
        if query:
            query_builder = query_builder.where(Memory.content.contains(query))

        query_builder = query_builder.order_by(Memory.importance.desc()).limit(limit)

        result = await self.db.execute(query_builder)
        memories = result.scalars().all()

        # 更新访问统计
        for memory in memories:
            memory.access_count += 1
            memory.last_accessed = datetime.utcnow()

        await self.db.commit()

        return memories

    async def extract_memory_from_conversation(
        self,
        conversation_id: int,
        user_id: int
    ) -> Optional[Memory]:
        """从对话中提取重要信息作为长期记忆"""
        # 读取对话历史
        # 使用LLM分析是否有值得记忆的信息
        # 提取并添加到记忆系统

        # 这里实现提取逻辑
        return None

    def _calculate_expiry(self, importance: float):
        """根据重要性计算过期时间"""
        from datetime import timedelta

        if importance > 0.8:
            return datetime.utcnow() + timedelta(days=180)  # 高重要：6个月
        elif importance > 0.6:
            return datetime.utcnow() + timedelta(days=90)  # 中重要：3个月
        elif importance > 0.4:
            return datetime.utcnow() + timedelta(days=30)  # 低重要：1个月
        else:
            return None  # 非常重要不过期

    async def cleanup_expired_memories(self, user_id: int = None):
        """清理过期记忆"""
        from sqlalchemy import select
        from models.memory import Memory
        from datetime import datetime

        query_builder = select(Memory).where(
            Memory.expires_at < datetime.utcnow(),
            Memory.is_active == True
        )

        if user_id:
            query_builder = query_builder.where(Memory.user_id == user_id)

        result = await self.db.execute(query_builder)
        expired_memories = result.scalars().all()

        for memory in expired_memories:
            memory.is_active = False

        await self.db.commit()

        return len(expired_memories)
