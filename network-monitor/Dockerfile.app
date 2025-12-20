# Dockerfile_app

# 使用精简 Python 镜像
FROM python:3.10-slim

# 安装必要系统依赖
RUN apt-get update && \
    apt-get install -y gcc libssl-dev libffi-dev curl && \
    rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制 Python 依赖文件
COPY requirements.txt ./

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY backend/ ./backend
COPY frontend/ ./frontend

# 时区环境变量（可选）
ENV TZ=Asia/Shanghai

# 暴露 Flask 端口
EXPOSE 5000

# 启动 Flask
CMD ["python", "backend/app.py"]
