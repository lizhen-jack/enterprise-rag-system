# Enterprise RAG System - 快速开始

> 企业级RAG系统：从零到部署只需5分钟

## 前置要求

- Python 3.9+
- pip包管理器
- (可选) Docker用于容器化部署

---

## 5分钟快速上手

### 🚀 方式1: 直接运行Python（推荐开发环境）

#### Step 1: 克隆项目

```bash
git clone https://github.com/lizhen-jack/enterprise-rag-system.git
cd enterprise-rag-system
```

#### Step 2: 安装依赖

```bash
pip install -r requirements.txt
```

如果requirements.txt不存在，手动安装核心依赖：

```bash
pip install fastapi uvicorn langchain chromadb python-multipart
```

#### Step 3: 启动后端服务

```bash
cd backend
python3 main.py
```

预期输出：
```
🚀 Enterprise RAG Backend starting...
✅ Documents loaded: 0
✅ Backend running on http://0.0.0.0:8000
```

#### Step 4: 启动前端服务（新终端）

```bash
cd frontend
python3 -m http.server 8001
```

#### Step 5: 访问Web界面

打开浏览器访问: http://localhost:8001

---

### 🐳 方式2: Docker部署（推荐生产环境）

#### Step 1: 创建Dockerfile（如果不存在）

在项目根目录创建 `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "backend/main.py", "--host", "0.0.0.0", "--port", "8080"]
```

#### Step 2: 构建Docker镜像

```bash
docker build -t enterprise-rag:latest .
```

#### Step 3: 运行容器

```bash
docker run -p 8080:8080 enterprise-rag:latest
```

---

## 上传文档与检索

### 通过Web界面（推荐）

1. 访问 http://localhost:8001
2. 点击"上传文档"按钮
3. 选择你的文档（支持PDF、TXT、DOCX）
4. 等待上传和索引完成
5. 在聊天框输入问题进行检索

---

### 通过API调用（集成到你的应用）

#### 上传文档

```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@/path/to/your/document.pdf"
```

响应：
```json
{
  "success": true,
  "document_id": "doc_12345",
  "chunks": 15
}
```

#### 提问检索

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "什么是RAG？"}'
```

响应：
```json
{
  "answer": "RAG (Retrieval-Augmented Generation) 是一种结合检索和生成的AI技术...",
  "sources": [
    {
      "content": "RAG系统的工作原理...",
      "doc_id": "doc_12345"
    }
  ]
}
```

---

## 常见问题

### Q1: 上传文档后显示undefined？

**A**: 这是前端小bug，已在v1.1修复。使用最新代码即可。

### Q2: Docker构建失败怎么办？

**A**: 确保Docker已安装并运行:
```bash
docker --version
docker ps
```

### Q3: 如何使用其他向量数据库？

**A**: 编辑 `backend/main.py` 中的 `ChromaDB` 配置，替换为 `Milvus`、`Pinecone`等。

### Q4: 能否部署到生产环境？

**A**: 可以！推荐使用：
- Nginx作为反向代理
- Gunicorn/Uvicorn作为ASGI服务器
- PostgreSQL/Redis作为缓存

---

## 示例文档

创建测试文档 `test_qa.txt`:

```
Q: 什么是企业级RAG系统？
A: 企业级RAG系统是针对企业内部文档和知识库的智能检索增强生成系统，能够快速准确地从海量的企业文档中找到相关信息并生成回答。

Q: RAG系统的核心组件有哪些？
A: RAG系统包含：
1. 文档上传与处理
2. 文本分块与向量化
3. 向量数据库存储
4. 语义搜索检索
5. 大模型生成回答

Q: 如何提高RAG系统的检索准确率？
A: 通过以下方式：
1. 优化文档分块策略
2. 使用高质量的Embedding模型
3. 精炼检索和生成的提示词
4. 添加知识蒸馏和微调
```

上传测试：
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@test_qa.txt"
```

---

## 生产部署建议

### 1. 反向代理配置 (Nginx)

```nginx
server {
    listen 80;
    server_name your-rag-system.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. ASGI服务器 (Uvicorn)

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. 监控与日志

- 使用 `Prometheus` 监控系统性能
- 使用 `ELK Stack` 收集和分析日志

---

## 下一步

- 查看完整[API文档](docs/API.md)
- 阅读系统架构[架构文档](docs/architecture.md)
- 参考部署[生产指南](docs/DEPLOYMENT.md)

---

_快速上手指南 | v1.0 | 2026-02-24_
_作者: 小龙（Little Dragon）_
