"""
RAG核心服务
集成：百度千帆API + Milvus向量库 + 长期记忆
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import redis
import requests
import json
from pymilvus import connections, Collection, utility, FieldSchema, CollectionSchema, DataType
import numpy as np

from core.config import settings


class BaiduEmbedding:
    """百度千帆嵌入模型"""

    def __init__(self):
        self.api_base = f"{settings.BAIYUN_API_BASE}/embeddings"
        self.api_key = settings.BAIYUN_API_KEY
        self.model = settings.EMBEDDING_MODEL
        self.dimension = settings.MILVUS_DIMENSION  # 百度embedding返回768维

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量生成文档向量"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            payload = {
                "model": self.model,
                "input": texts
            }

            response = requests.post(self.api_base, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            data = response.json()
            embeddings = [item["embedding"] for item in data["data"]]

            return embeddings

        except Exception as e:
            print(f"Embedding生成失败: {e}")
            # 返回零向量作为fallback
            return [[0.0] * self.dimension] * len(texts)

    async def embed_query(self, text: str) -> List[float]:
        """生成查询向量"""
        embeddings = await self.embed_documents([text])
        return embeddings[0] if embeddings else [0.0] * self.dimension


class BaiduChat:
    """百度千帆对话模型"""

    def __init__(self):
        self.api_base = f"{settings.BAIYUN_API_BASE}/chat/{settings.CHAT_MODEL}"
        self.api_key = settings.BAIYUN_API_KEY
        self.model = settings.CHAT_MODEL

    async def chat(
        self,
        messages: List[Dict],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """对话生成"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            payload = {
                "messages": messages,
                "temperature": temperature,
                "max_output_tokens": max_tokens
            }

            response = requests.post(self.api_base, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            data = response.json()
            return data.get("result", "")

        except Exception as e:
            print(f"百度千帆API调用失败: {e}")
            return f"抱歉，AI回复生成失败：{str(e)}"


class MilvusService:
    """Milvus向量数据库服务"""

    def __init__(self):
        self.host = settings.MILVUS_HOST
        self.port = settings.MILVUS_PORT
        self.collection_name = settings.MILVUS_COLLECTION
        self.dimension = settings.MILVUS_DIMENSION

        # 连接Milvus
        self._connect()
        self._init_collection()

    def _connect(self):
        """连接Milvus"""
        connections.connect(
            alias="default",
            host=self.host,
            port=self.port
        )

    def _init_collection(self):
        """初始化Collection"""
        if utility.has_collection(self.collection_name):
            self.collection = Collection(self.collection_name)
        else:
            # 创建Schema
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="chunk_id", dtype=DataType.INT64),
                FieldSchema(name="user_id", dtype=DataType.INT64),
                FieldSchema(name="document_id", dtype=DataType.INT64),
                FieldSchema(name="file_name", dtype=DataType.VARCHAR, max_length=255),
                FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dimension),
                FieldSchema(name="created_at", dtype=DataType.VARCHAR, max_length=50)
            ]

            schema = CollectionSchema(
                fields=fields,
                description="Enterprise RAG文档向量数据"
            )

            # 创建Collection
            self.collection = Collection(
                name=self.collection_name,
                schema=schema
            )

            # 创建索引（IVF_FLAT）
            index_params = {
                "index_type": "IVF_FLAT",
                "metric_type": "COSINE",
                "params": {"nlist": 128}
            }

            self.collection.create_index(
                field_name="embedding",
                index_params=index_params
            )

            print(f"✅ Milvus Collection '{self.collection_name}' 创建成功")

    async def insert_chunks(
        self,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ) -> int:
        """插入文档块"""
        if not chunks or not embeddings:
            return 0

        # 准备数据
        chunk_ids = [chunk["chunk_id"] for chunk in chunks]
        user_ids = [chunk["user_id"] for chunk in chunks]
        document_ids = [chunk["document_id"] for chunk in chunks]
        file_names = [chunk["file_name"] for chunk in chunks]
        contents = [chunk["content"] for chunk in chunks]
        created_at = [datetime.utcnow().isoformat() for _ in chunks]

        data = [
            chunk_ids,
            user_ids,
            document_ids,
            file_names,
            contents,
            embeddings,
            created_at
        ]

        # 插入Milvus
        self.collection.insert(data)
        self.collection.flush()

        return len(chunks)

    async def search(
        self,
        query_embedding: List[float],
        user_id: int,
        top_k: int = 5,
        document_ids: List[int] = None
    ) -> List[Dict[str, Any]]:
        """向量搜索"""
        # 加载Collection到内存
        self.collection.load()

        # 构建搜索表达式
        expr = f"user_id == {user_id}"
        if document_ids:
            ids_str = ",".join(map(str, document_ids))
            expr += f" and document_id in [{ids_str}]"

        # 执行搜索
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 10}
        }

        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            expr=expr,
            output_fields=["chunk_id", "user_id", "document_id", "file_name", "content"]
        )

        # 格式化结果
        formatted_results = []
        for hit in results[0]:
            if hit.score < settings.SIMILARITY_THRESHOLD:
                continue

            formatted_results.append({
                "chunk_id": hit.entity.get("chunk_id"),
                "document_id": hit.entity.get("document_id"),
                "file_name": hit.entity.get("file_name"),
                "content": hit.entity.get("content"),
                "score": hit.score
            })

        return formatted_results

    async def delete_by_document(self, document_id: int):
        """删除文档的所有向量"""
        expr = f"document_id == {document_id}"
        self.collection.delete(expr)
        self.collection.flush()


class RAGService:
    """RAG检索增强生成服务（完整集成）"""

    def __init__(self, db):
        self.db = db
        self.embedding = BaiduEmbedding()
        self.chat = BaiduChat()
        self.milvus = MilvusService()

        # Redis缓存
        self.redis = redis.from_url(settings.REDIS_URL)

    async def index_document(
        self,
        document_id: int,
        user_id: int,
        file_name: str,
        chunks: List[str]
    ) -> int:
        """索引文档到向量库"""
        if not chunks:
            return 0

        # 生成向量
        embeddings = await self.embedding.embed_documents(chunks)

        # 准备chunk数据
        chunk_data = []
        for idx, chunk in enumerate(chunks):
            chunk_data.append({
                "chunk_id": int(hash(f"{document_id}_{idx}") % (10 ** 9)),
                "user_id": user_id,
                "document_id": document_id,
                "file_name": file_name,
                "content": chunk
            })

        # 插入Milvus
        count = await self.milvus.insert_chunks(chunk_data, embeddings)

        # 清除缓存
        self._clear_search_cache(user_id)

        return count

    async def search(
        self,
        query: str,
        user_id: int,
        top_k: int = 5,
        document_ids: List[int] = None,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """语义检索"""
        # 检查缓存
        cache_key = f"search:{user_id}:{hash(query)}:{top_k}"
        if use_cache:
            cached = self.redis.get(cache_key)
            if cached:
                return json.loads(cached)

        # 生成查询向量
        query_embedding = await self.embedding.embed_query(query)

        # 向量搜索
        results = await self.milvus.search(query_embedding, user_id, top_k, document_ids)

        # 缓存结果（5分钟）
        if use_cache:
            self.redis.setex(cache_key, 300, json.dumps(results))

        return results

    async def chat(
        self,
        query: str,
        user_id: int,
        conversation_history: List[Dict],
        user_prompt: str = "",
        document_ids: List[int] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """RAG对话"""
        # 1. 检索相关文档
        search_results = await self.search(query, user_id, document_ids=document_ids)

        # 2. 构建上下文
        context = ""
        if search_results:
            context += "**以下是从文档中检索到的相关信息：**\n\n"
            for idx, result in enumerate(search_results, 1):
                context += f"[来源{idx}] {result['file_name']}\n"
                context += f"{result['content']}\n"
                context += f"(相似度: {result['score']:.2%})\n\n"
        else:
            context = "（文档检索未找到相关信息）"

        # 3. 添加用户提示
        if user_prompt:
            context += f"\n**用户补充说明：**\n{user_prompt}\n"

        # 4. 构建消息历史
        system_prompt = f"""你是一个专业的企业知识助手，擅长利用企业文档回答问题。

**工作原则：**
1. 优先基于检索到的文档信息回答
2. 如果文档中没有相关信息，明确说明"文档中没有相关内容"
3. 回答要准确、简洁、专业
4. 必须引用具体的文档来源
5. 保持与对话历史的一致性

**当前上下文：**
{context}

现在开始回答用户的问题。"""

        messages = [{"role": "system", "content": system_prompt}]

        # 添加历史对话（最近10轮）
        for msg in conversation_history[-10:]:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })

        # 添加当前问题
        messages.append({"role": "user", "content": query})

        # 5. 生成回复
        response = await self.chat.chat(messages, temperature)

        return {
            "response": response,
            "sources": [
                {
                    "file_name": r["file_name"],
                    "content": r["content"],
                    "score": r["score"]
                } for r in search_results
            ],
            "context": context
        }

    def _clear_search_cache(self, user_id: int):
        """清除搜索缓存"""
        pattern = f"search:{user_id}:*"
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)


class MemoryService:
    """长期记忆服务（参考OpenClaw）"""

    def __init__(self, db):
        self.db = db

    async def add_memory(
        self,
        user_id: int,
        content: str,
        importance: float = 0.5,
        category: str = None,
        source: str = "manual",
        tags: List[str] = None
    ) -> Dict:
        """添加长期记忆"""
        from models.memory import Memory

        memory = Memory(
            user_id=user_id,
            content=content,
            importance=importance,
            category=category or "general",
            source=source,
            tags=tags or [],
            expires_at=self._calculate_expiry(importance)
        )

        self.db.add(memory)
        await self.db.commit()
        await self.db.refresh(memory)

        return {
            "id": memory.id,
            "content": memory.content,
            "importance": memory.importance,
            "category": memory.category,
            "tags": memory.tags,
            "expires_at": memory.expires_at
        }

    async def retrieve_memories(
        self,
        user_id: int,
        query: str = None,
        category: str = None,
        min_importance: float = 0.7,
        limit: int = 5
    ) -> List[Dict]:
        """检索长期记忆"""
        from sqlalchemy import select, or_
        from models.memory import Memory

        query_builder = select(Memory).where(
            Memory.user_id == user_id,
            Memory.is_active == True,
            Memory.importance >= min_importance
        )

        if category:
            query_builder = query_builder.where(Memory.category == category)

        # 关键词搜索
        if query:
            words = query.split()
            conditions = [Memory.content.contains(word) for word in words]
            query_builder = query_builder.where(or_(*conditions))

        query_builder = query_builder.order_by(Memory.importance.desc()).limit(limit)

        result = await self.db.execute(query_builder)
        memories = result.scalars().all()

        # 更新访问统计
        for memory in memories:
            memory.access_count += 1
            memory.last_accessed = datetime.utcnow()

        await self.db.commit()

        return [
            {
                "id": m.id,
                "content": m.content,
                "importance": m.importance,
                "category": m.category,
                "tags": m.tags,
                "source": m.source,
                "access_count": m.access_count
            }
            for m in memories
        ]

    def _calculate_expiry(self, importance: float):
        """根据重要性计算过期时间"""
        if importance > 0.9:
            return datetime.utcnow() + timedelta(days=180)
        elif importance > 0.8:
            return datetime.utcnow() + timedelta(days=90)
        elif importance > 0.7:
            return datetime.utcnow() + timedelta(days=30)
        elif importance > 0.6:
            return datetime.utcnow() + timedelta(days=7)
        else:
            return None  # 不过期

    async def cleanup_expired_memories(self, user_id: int = None):
        """清理过期记忆"""
        from sqlalchemy import select
        from models.memory import Memory

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
