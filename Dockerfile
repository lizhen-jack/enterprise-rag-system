FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt || \
    pip install fastapi uvicorn python-multipart pydantic

# 复制项目文件
COPY backend/ backend/
COPY docs/ docs/

# 暴露端口
EXPOSE 8000

# 启动服务
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
