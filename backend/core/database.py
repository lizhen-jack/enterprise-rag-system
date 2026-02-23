"""
数据库初始化和连接管理
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import SQLModel

from core.config import settings

# 创建异步引擎
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

# 创建会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    """初始化数据库表"""
    async with engine.begin() as conn:
        # 这里的导入必须在这里，避免循环依赖
        from models.user import User
        from models.document import Document
        from models.memory import Memory
        from models.conversation import Conversation, Message

        await conn.run_sync(SQLModel.metadata.create_all)


async def get_db() -> AsyncSession:
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
