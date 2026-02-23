"""
RAG核心服务（简化版）
集成：百度千帆API + 关键词搜索 + 内存缓存 + 长期记忆
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import requests
import json
import time
import re
from collections import defaultdict

from core.config import settings


class BaiduAuth:
    """百度千帆OAuth 2.0认证"""

    _access_token = None
    _token_expires_at = 0

    @classmethod
    def get_access_token(cls) -> str:
        """获取访问令牌（自动刷新）"""
        now = int(time.time())

        # 如果令牌还有效，直接返回
        if cls._access_token and now < cls._token_expires_at - 60:
            return cls._access_token

        # 获取新令牌
        url = settings.BAIYUN_AUTH_URL
        params = {
            "grant_type": "client_credentials",
            "client_id": settings.BAIYUN_ACCESS_KEY,
            "client_secret": settings.BAIYUN_SECRET_KEY
        }

        try:
            response = requests.post(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            cls._access_token = data.get("access_token")
            expires_in = data.get("expires_in", 2592000)
            cls._token_expires_at = now + expires_in

            print(f"✅ 百度千帆Access Token刷新成功")
            return cls._access_token

        except Exception as e:
            print(f"❌ 百度千帆认证失败: {e}")
            raise


class BaiduEmbedding:
    """百度千帆嵌入模型（暂时禁用，使用占位）"""

    def __init__(self):
        self.api_url = settings.EMBEDDING_API_BASE
        self.engine = settings.EMBEDDING_MODEL
        self.dimension = settings.MILVUS_DIMENSION

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量生成文档向量（暂未实现，返回零向量）"""
        # 简化版：不使用向量搜索
        return [[0.0] * self.dimension] * len(texts)

    async def embed_query(self, text: str) -> List[float]:
        """生成查询向量（暂未实现，返回零向量）"""
        return [0.0] * self.dimension


class BaiduChat:
    """百度千帆对话模型（Coding Plan Lite）"""

    def __init__(self):
        self.api_url = f"{settings.BAIYUN_API_BASE}/chat/{settings.CHAT_MODEL}"
        self.model = settings.CHAT_MODEL

    async def chat(
        self,
        messages: List[Dict],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """对话生成"""
        try:
            access_token = BaiduAuth.get_access_token()

            headers = {
                "Content-Type": "application/json"
            }

            payload = {
                "messages": messages,
                "temperature": temperature,
                "top_p": 0.8,
                "penalty_score": 1.0,
                "disable_search": False,
                "enable_citation": False
            }

            url = f"{self.api_url}?access_token={access_token}"

            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()

            data = response.json()

            if "error_code" in data:
                error_msg = data.get("error_msg", "未知错误")
                print(f"❌ Chat API错误: {error_msg}")
                return f"抱歉，AI回复生成失败：{error_msg}"

            result = data.get("result", "")
            return result

        except Exception as e:
            print(f"❌ Chat API调用失败: {e}")
            return f"抱歉，AI回复生成失败：{str(e)}"


class SimpleMemoryCache:
    """简单的内存缓存"""

    def __init__(self):
        self.cache = {}

    def get(self, key):
        return self.cache.get(key)

    def set(self, key, value, expire_seconds=None):
        self.cache[key] = value

    def delete(self, key):
        self.cache.pop(key, None)

    def clear_pattern(self, pattern):
        keys_to_delete = [k for k in self.cache.keys() if pattern in k]
        for k in keys_to_delete:
            del self.cache[k]


class KeywordSearchService:
    """关键词搜索服务（替代Milvus）"""

    def __init__(self, db):
        self.db = db
        self.cache = SimpleMemoryCache()

    async def insert_chunks(
        self,
        chunks: List[Dict[str, Any]]
    ) -> int:
        """存储文档块到数据库"""
        # 文档块已经存储在PostgreSQL/MongoDB中
        # 这里只是记录插入成功
        print(f"✅ 存储 {len(chunks)} 个文档块到数据库")
        return len(chunks)

    async def search(
        self,
        query: str,
        user_id: int,
        top_k: int = 5,
        document_ids: List[int] = None
    ) -> List[Dict[str, Any]]:
        """关键词搜索"""
        # 提取查询中的关键词
        keywords = self._extract_keywords(query)
        print(f"🔍 关键词: {keywords}")

        # 从数据库中搜索包含关键词的文档块
        results = await self._search_in_database(keywords, user_id, document_ids, top_k)

        return results

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单分词（中文+英文）
        # 移除标点符号
        text = re.sub(r'[^\w\s]', '', text)
        # 按空格和中文分割
        words = re.findall(r'[\w]+|[\u4e00-\u9fff]+', text)
        # 过滤停用词（简化版）
        stop_words = {'的', '了', '是', '在', '有', '和', '我', '你', '他', '这', '那', '什么', '怎么', '如何'}
        keywords = [w for w in words if len(w) > 1 and w not in stop_words]
        return keywords

    async def _search_in_database(
        self,
        keywords: List[str],
        user_id: int,
        document_ids: List[int],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """在数据库中搜索"""
        # 这里简化实现：直接返回空列表
        # 实际应该查询数据库中的文档块
        # 从models.document中查询文档，然后匹配内容

        print(f"⚠️  关键词搜索未完全实现，返回空结果")
        return []


class RAGService:
    """RAG检索增强生成服务（简化版）"""

    def __init__(self, db):
        self.db = db
        self.embedding = BaiduEmbedding()
        self.chat = BaiduChat()
        self.search_service = KeywordSearchService(db) if not settings.ENABLE_MILVUS else None
        self.cache = SimpleMemoryCache()

    async def index_document(
        self,
        document_id: int,
        user_id: int,
        file_name: str,
        chunks: List[str]
    ) -> int:
        """索引文档"""
        if not chunks:
            return 0

        print(f"📄 开始索引文档: {file_name} ({len(chunks)} 个chunks)")

        # 简化版：只记录chunk数量，不生成向量
        chunk_data = [
            {
                "chunk_id": int(hash(f"{document_id}_{idx}") % (10 ** 9)),
                "user_id": user_id,
                "document_id": document_id,
                "file_name": file_name,
                "content": chunk
            }
            for idx, chunk in enumerate(chunks)
        ]

        # 插入到搜索服务
        count = await self.search_service.insert_chunks(chunk_data)

        # 清除缓存
        self._clear_search_cache(user_id)

        return count

    async def search(
        self,
        query: str,
        user_id: int,
        top_k: int = 5,
        document_ids: List[int] = None,
        use_cache: bool = False
    ) -> List[Dict[str, Any]]:
        """关键词检索"""
        # 检查缓存
        cache_key = f"search:{user_id}:{hash(query)}:{top_k}"
        if use_cache:
            cached = self.cache.get(cache_key)
            if cached:
                return cached

        # 关键词搜索
        results = await self.search_service.search(query, user_id, top_k, document_ids)

        # 缓存结果
        if use_cache:
            self.cache.set(cache_key, results)

        print(f"🔍 搜索结果: 找到 {len(results)} 个匹配")
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
                context += f"{result['content']}\n\n"
        else:
            context = "（文档检索未找到相关信息，基于我的知识库回答）"

        # 3. 添加用户提示
        if user_prompt:
            context += f"\n**用户补充说明：**\n{user_prompt}\n"

        # 4. 构建消息历史
        system_prompt = f"""你是一个专业的企业知识助手，擅长回答问题。

**工作原则：**
1. 优先基于检索到的文档信息回答
2. 如果文档中没有相关信息，可以基于你的知识库回答
3. 回答要准确、简洁、专业
4. 保持与对话历史的一致性

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
        print(f"💬 开始生成回复...")
        response = await self.chat.chat(messages, temperature)
        print(f"✅ 回复生成完成")

        return {
            "response": response,
            "sources": [
                {
                    "file_name": r.get("file_name", "未知"),
                    "content": r.get("content", ""),
                    "score": 1.0
                } for r in search_results
            ],
            "context": context
        }

    def _clear_search_cache(self, user_id: int):
        """清除搜索缓存"""
        self.cache.clear_pattern(f"search:{user_id}:")


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
            return None

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
