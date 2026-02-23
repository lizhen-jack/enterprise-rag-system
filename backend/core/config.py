"""
系统配置管理
支持：百度千帆API + Milvus向量库
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """系统配置"""

    # 应用配置
    APP_NAME: str = "Enterprise RAG System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://postgres:rag_password@localhost/rag_db"

    # 向量数据库配置（Milvus）
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_COLLECTION: str = "enterprise_rag"
    MILVUS_DIMENSION: int = 768  # BGE向量的维度

    # Redis配置（缓存和任务队列）
    REDIS_URL: str = "redis://localhost:6379/0"

    # 百度千帆API配置
    # 格式: https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{model}
    BAIYUN_API_KEY: str = ""  # 格式: {API_KEY}.{SECRET_KEY}
    BAIYUN_API_BASE: str = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop"
    EMBEDDING_MODEL: str = "embedding-v1"
    CHAT_MODEL: str = "ernie-speed-128k"

    # OpenAI兼容接口（百度千帆也支持）
    OPENAI_API_BASE: str = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1"
    OPENAI_API_KEY: str = ""  # 百度千帆的API Key

    # 文档处理配置
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: list = ["pdf", "docx", "txt", "md", "xlsx", "xls"]
    UPLOAD_DIR: str = "./uploads"
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50

    # RAG配置
    TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.6  # 相似度阈值

    # 长期记忆配置（参考OpenClaw）
    MEMORY_MAX_ENTRIES: int = 1000
    MEMORY_RETENTION_DAYS: int = 90
    MEMORY_LOW_IMPORTANCE: float = 0.7  # 低重要性过滤

    # JWT配置
    SECRET_KEY: str = "rag-secret-key-2024-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时

    # CORS配置
    CORS_ORIGINS: list = ["http://localhost:80", "http://localhost", "http://120.48.89.60"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
