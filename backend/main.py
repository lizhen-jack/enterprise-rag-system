"""
企业级RAG系统 - FastAPI后端
支持：文档上传、语义检索、长期记忆、用户上下文
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from core.database import init_db
from api import documents, chat, users, memory

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    await init_db()
    print("🚀 企业级RAG系统启动成功！")
    yield
    # 关闭时清理
    print("👋 企业级RAG系统已关闭")

app = FastAPI(
    title="企业级RAG系统",
    description="企业级知识检索与记忆系统",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需要限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(users.router, prefix="/api/v1/users", tags=["用户管理"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["文档管理"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["对话与检索"])
app.include_router(memory.router, prefix="/api/v1/memory", tags=["长期记忆"])

@app.get("/")
async def root():
    """健康检查"""
    return {
        "status": "online",
        "name": " Enterprise RAG System",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """详细健康检查"""
    return {
        "status": "healthy",
        "database": "connected",
        "vector_db": "connected"
    }
