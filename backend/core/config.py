"""
系统配置管理
支持：环境变量+配置文件
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
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost/rag_db"

    # 向量数据库配置
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_COLLECTION: str = "enterprise_rag"

    # Redis配置（缓存和任务队列）
    REDIS_URL: str = "redis://localhost:6379/0"

    # AI模型配置
    # 使用国内API（通义千问/文心一言），兼容OpenAI格式
    AI_API_BASE: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    AI_API_KEY: str = ""
    EMBEDDING_MODEL: str = "text-embedding-v2"
    CHAT_MODEL: str = "qwen-plus"

    # 文档处理配置
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: list = ["pdf", "docx", "txt", "md", "xlsx"]
    UPLOAD_DIR: str = "./uploads"

    # RAG配置
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50
    TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.6

    # 长期记忆配置
    MEMORY_MAX_ENTRIES: int = 1000
    MEMORY_RETENTION_DAYS: int = 90
    SESSION_MAX_MESSAGES: int = 50

    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
