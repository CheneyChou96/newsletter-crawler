# 使用官方 Python 镜像
FROM python:3.11-slim-bookworm

# 安装构建工具链（如有需要）
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc musl-dev && \
    rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 从外部镜像复制 uv（快速 Python 包管理器）
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 复制项目文件
COPY . .

# 安装依赖
RUN uv sync

# 暴露服务端口
EXPOSE 3001

# 启动应用
CMD ["uv", "run", "main.py"]
