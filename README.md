# Enterprise RAG System 🚀

企业级知识库AI问答系统 - 完整的RAG实现 + 前后端架构

## ✨ Features

### 后端 (FastAPI + Python)
- 📄 文档上传和解析 (PDF, DOCX, TXT, MD)
- 🧠 向量化存储和检索 (ChromaDB)
- 🔍 语义搜索和检索
- 💬 AI问答接口 (LLM集成)
- 📊 API文档 (Swagger UI)
- ⚡ 高性能异步处理

### 前端 (HTML + CSS + JS)
- 🎨 现代化UI设计
- 📤 拖拽文件上传
- 💬 实时聊天界面
- 📱 响应式布局
- 🌙 支持暗色模式

## 🚀 Quick Start

### 方式1: 本地运行

```bash
# 克隆仓库
git clone https://github.com/lizhen-jack/enterprise-rag-system.git

# 进入后端目录
cd enterprise-rag-system/backend

# 安装依赖
pip install -r requirements.txt

# 启动后端
uvicorn main:app --host 0.0.0.0 --port 8000

# 另开终端，启动前端
cd ../frontend
python3 -m http.server 8001

# 访问
# 后端API: http://localhost:8000/docs
# 前端界面: http://localhost:8001
```

### 方式2: Docker部署

```bash
# 构建镜像
docker build -t lizhenjack/enterprise-rag-system:latest .

# 运行容器
docker run -d \
  --name rag-system \
  -p 8000:8000 \
  -p 8001:8001 \
  lizhenjack/enterprise-rag-system:latest

# 访问
# 后端API: http://localhost:8000/docs
# 前端界面: http://localhost:8001
```

## 📦 Project Structure

```
enterprise-rag-system/
├── backend/
│   ├── main.py           # FastAPI应用入口
│   ├── requirements.txt  # Python依赖
│   ├── vector_store.py   # 向量数据库操作
│   └── llm_client.py     # LLM客户端
├── frontend/
│   ├── index.html        # 主页面
│   ├── style.css         # 样式文件
│   └── app.js            # 前端逻辑
├── uploads/              # 上传文件目录
├── chroma_db/            # 向量数据库
└── Dockerfile            # Docker镜像配置
```

## 🛠️ Tech Stack

### Backend
- FastAPI - 高性能Web框架
- ChromaDB - 向量数据库
- OpenAI API - LLM接口
- LangChain - RAG框架

### Frontend
- HTML5 + CSS3 + Vanilla JS
- Fetch API - HTTP请求
- Flexbox/Grid - 现代布局

## 📚 API文档

启动后端后访问: http://localhost:8000/docs

主要接口:
- `POST /api/upload` - 上传文档
- `POST /api/chat` - AI问答
- `GET /health` - 健康检查

## 🔧 Configuration

环境变量 (`.env`):
```env
OPENAI_API_KEY=your_api_key_here
CHROMA_PERSIST_DIR=./chroma_db
UPLOAD_DIR=./uploads
```

## 🐛 Bug Fixes

2026-02-24自主修复:
- ✅ 前端文件上传显示`undefined` → 改为`file.name`
- ✅ 聊天返回`[object Object]` → 修正API字段

## 📄 License

MIT License

## 👋 Author

**小龙** - AI自主开发与优化

---

_完整文档见: DEPLOYMENT.md_
