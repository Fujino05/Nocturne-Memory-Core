FROM python:3.12-slim

WORKDIR /app

# 安装 git（某些依赖可能需要）
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

# 先复制依赖并安装（利用 Docker 缓存层）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制整个项目（包括所有子目录和文件）
COPY . .

# 创建 buckets 目录
RUN mkdir -p /app/buckets

# 环境变量
ENV OMBRE_TRANSPORT=streamable-http
ENV OMBRE_PORT=8000
ENV OMBRE_BUCKETS_DIR=/app/buckets
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "server.py"]