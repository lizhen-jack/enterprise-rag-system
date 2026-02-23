"""
系统配置管理
简化部署版本：SQLite + 关键词搜索（替代Milvus）
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """系统配置"""

    # 应用配置
    APP_NAME: str = "Enterprise RAG System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True  # 开发环境

    # 数据库配置（SQLite简化版）
    DATABASE_URL: str = "sqlite+aiosqlite:///./rag.db"

    # 向量数据库配置（禁用Milvus，使用关键词搜索）
    ENABLE_MILVUS: bool = False
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_COLLECTION: str = "enterprise_rag"
    MILVUS_DIMENSION: int = 768

    # Redis配置（禁用，使用内存缓存）
    ENABLE_REDIS: bool = False
    REDIS_URL: str = "redis://localhost:6379/0"

    # 百度千帆API配置（Coding Plan Lite）
    BAIYUN_API_KEY: str = ""
    BAIYUN_ACCESS_KEY: str = ""
    BAIYUN_SECRET_KEY: str = ""
    CHAT_MODEL: str = "qianfan-code-latest"
    BAIYUN_API_BASE: str = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop"
    EMBEDDING_MODEL: str = "embedding-v1"
    EMBEDDING_API_BASE: str = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/embeddings/embedding-v1"

    # 文档处理配置
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: list = ["pdf", "docx", "txt", "md", "xlsx", "xls"]
    UPLOAD_DIR: str = "./uploads"
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50

    # RAG配置
    TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.0  # 关键词搜索不使用相似度阈值

    # 长期记忆配置
    MEMORY_MAX_ENTRIES: int = 1000
    MEMORY_RETENTION_DAYS: int = 90
    MEMORY_LOW_IMPORTANCE: float = 0.7

    # JWT配置
    SECRET_KEY: str = "rag-secret-key-2024-production-lizhen"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天

    # CORS配置（允许外网访问）
    CORS_ORIGINS: list = ["http://localhost", "http://localhost:80", "http://120.48.89.60"]

    # 百度千帆认证服务器
    BAIYUN_AUTH_URL: str = "https://aip.baidubce.com/oauth/2.0/token"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# 解析API Key（格式: {API_KEY}.{SECRET_KEY}）
if settings.BAIYUN_API_KEY:
    parts = settings.BAIYUN_API_KEY.split('.')
    if len(parts) == 2:
        settings.BAIYUN_ACCESS_KEY = parts[0]
        settings.BAIYUN_SECRET_KEY = parts[1]
        print(f"✅ 百度千帆API Key已配置: {settings.BAIYUN_ACCESS_KEY[:10]}...")
    else:
        print("⚠️  百度千帆API Key格式不正确，应为 {API_KEY}.{SECRET_KEY}")
else:
    print("⚠️  未配置百度千帆API Key，某些功能将不可用")
