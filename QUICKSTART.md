# 快速开始

## 本地开发

### 后端
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### 前端
```bash
cd frontend
npm install
npm run dev
```

### 向量数据库（Milvus）
```bash
docker-compose -f docker/milvus.yml up -d
```

## Docker部署

```bash
docker-compose up -d
```

访问：http://localhost:80
