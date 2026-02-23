# 企业级RAG系统 [![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org) [![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com) [![Vue 3](https://img.shields.io/badge/Vue-3.4-42b883.svg)](https://vuejs.org) [![Milvus](https://img.shields.io/badge/Milvus-Latest-orange.svg)](https://milvus.io)

> 基于国内主流技术栈的企业级知识检索与长期记忆系统

## ✨ 特性

- 🔍 **语义检索**：基于向量数据库的智能文档检索
- 🧠 **长期记忆**：参考OpenClaw的记忆管理方法，支持用户上下文的持续记忆
- 📄 **文档管理**：支持PDF、Word、Excel、TXT等多种格式
- 💬 **智能对话**：集成RAG（检索增强生成）提供精准问答
- 🏢 **企业级**：支持多用户、权限管理、数据隔离
- 🎨 **现代化UI**：基于Vue 3 + Element Plus的优雅界面
- 🚀 **高性能**：异步架构 + Milvus向量数据库

## 🏗️ 技术栈

### 后端
- **Web框架**: FastAPI 0.109
- **向量数据库**: Milvus (国产高性能向量数据库)
- **关系数据库**: PostgreSQL 15
- **缓存**: Redis 7
- **AI模型**: 通义千问/文心一言 (支持OpenAI兼容接口)
- **AI框架**: LangChain 0.1.5

### 前端
- **框架**: Vue 3.4 (Composition API)
- **组件库**: Element Plus 2.5
- **状态管理**: Pinia 2.1
- **路由**: Vue Router 4.2
- **构建工具**: Vite 5.0

## 📦 安装与部署

### 方式1：Docker Compose (推荐)

```bash
# 克隆项目
git clone https://github.com/lizhen-jack/enterprise-rag-system
cd enterprise-rag-system

# 启动所有服务
docker-compose up -d

# 访问应用
# 前端: http://localhost
# 后端API: http://localhost:8000
# API文档: http://localhost:8000/docs
```

### 方式2：手动部署

#### 后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量 (复制.env.example为.env，填写API密钥)
cp .env.example .env

# 初始化数据库
python -m alembic upgrade head

# 启动服务
uvicorn main:app --reload --port 8000
```

#### 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

## 📚 核心功能

### 1. 文档管理
- 📤 支持多种文件格式上传 (PDF/DOCX/TXT/MD/XLSX)
- 🔄 自动文档解析与分块
- 🔎 实时索引状态监控

### 2. 智能检索 (RAG)
- 🎯 基于Milvus的高性能向量检索
- 📊 精确度 + 召回率优化
- 🏷️ 来源追溯（文档标题、段落信息）

### 3. 长期记忆系统
- 💎 借鉴OpenClaw的记忆方法论
- ⭐ 重要性分级（0-1评分）
- 🗂️ 分类管理
- 📝 标签系统
- ⏰ 自动过期清理

### 4. 对话管理
- 💬 多会话支持
- 📜 完整对话历史
- 🧠 融合文档检索 + 长期记忆

## 🎯 应用场景

- 🏢 企业知识库管理
- 📚 技术文档问答
- 💼 客户服务智能回复
- 🎓 教育机构资料检索
- 🔬 研究机构文献管理

## 📁 项目结构

```
enterprise-rag-system/
├── backend/              # 后端服务
│   ├── api/             # API路由
│   ├── core/            # 核心配置
│   ├── models/          # 数据模型
│   ├── services/        # 业务逻辑
│   └── utils/           # 工具函数
├── frontend/            # 前端应用
│   ├── src/
│   │   ├── views/       # 页面组件
│   │   ├── stores/      # Pinia状态
│   │   ├── api/         # API封装
│   │   └── router/      # 路由配置
├── docker/              # Docker配置
├── docs/                # 项目文档
└── docker-compose.yml   # 容器编排
```

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发流程

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📝 待办事项

- [ ] Milvus向量存储完整实现
- [ ] 对话上下文的长期记忆自动提取
- [ ] 文档OCR识别（图片/PDF扫描件）
- [ ] 多轮对话的上下文优化
- [ ] 权限管理系统（用户/部门）
- [ ] 审计日志功能
- [ ] API限流与安全防护

## 📄 开源协议

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com) - 现代的Python Web框架
- [Milvus](https://milvus.io) - 开源向量数据库
- [LangChain](https://langchain.com) - AI应用开发框架
- [Vue 3](https://vuejs.org) - 渐进式JavaScript框架
- [Element Plus](https://element-plus.org) - Vue 3组件库
- [OpenClaw](https://github.com/openclaw/openclaw) - 记忆系统灵感来源

## 💬 联系方式

- 项目作者: 李祯 (小龙)
- Email: 762187599@qq.com
- GitHub: [@lizhen-jack](https://github.com/lizhen-jack)

---

⭐ 如果这个项目对您有帮助，请给个Star支持一下！
