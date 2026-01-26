# AeroVision Label System - Dockerfile
# 支持 GPU (CUDA) 和 CPU 推理
#
# 构建方式:
#   GPU 版本: docker build --build-arg DEVICE=gpu -t aerovision:gpu .
#   CPU 版本: docker build --build-arg DEVICE=cpu -t aerovision:cpu .

# ==================== 构建参数 ====================
ARG DEVICE=gpu
ARG CUDA_VERSION=12.6
ARG PYTHON_VERSION=3.12

# ==================== 基础镜像选择 ====================
FROM nvidia/cuda:${CUDA_VERSION}.0-cudnn9-runtime-ubuntu22.04 AS base-gpu
FROM python:${PYTHON_VERSION}-slim AS base-cpu

# 根据 DEVICE 参数选择基础镜像
FROM base-${DEVICE} AS base

# ==================== 构建阶段 ====================
WORKDIR /app

# 重新声明 ARG（FROM 之后需要重新声明）
ARG DEVICE=gpu

# 环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    # 应用配置
    IMAGES_DIR=/app/images \
    LABELED_DIR=/app/labeled \
    DATABASE_PATH=/app/data/labels.db \
    AI_CONFIG_PATH=/app/config.yaml \
    # OCR API 地址（默认值，可通过 docker-compose 覆盖）
    OCR_API_URL=http://localhost:8000/v2/models/ocr/infer \
    # CPU 推理线程限制
    OMP_NUM_THREADS=4 \
    MKL_NUM_THREADS=4 \
    OPENBLAS_NUM_THREADS=4 \
    NUMEXPR_NUM_THREADS=4 \
    TORCH_NUM_THREADS=4 \
    CPU_NUM=4 \
    # 国内镜像源
    PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

# GPU 镜像需要安装 Python
RUN if [ "$DEVICE" = "gpu" ]; then \
        apt-get update && \
        apt-get install -y --no-install-recommends \
            python3 python3-pip python3-dev && \
        ln -sf /usr/bin/python3 /usr/bin/python && \
        ln -sf /usr/bin/pip3 /usr/bin/pip; \
    fi

# 更换 apt 源为清华镜像（仅 CPU 镜像）
RUN if [ "$DEVICE" = "cpu" ]; then \
        sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || true && \
        sed -i 's|security.debian.org|mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || true; \
    fi

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        curl \
        libgl1-mesa-glx \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgomp1 \
        libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt ./

# 升级 pip
RUN pip install --no-cache-dir --upgrade pip

# 安装 PyTorch（根据 DEVICE 选择版本）
RUN if [ "$DEVICE" = "gpu" ]; then \
        echo "Installing PyTorch GPU (CUDA 12.6)..." && \
        pip install --no-cache-dir torch==2.9.1 torchvision==0.24.1 \
            -f https://mirrors.aliyun.com/pytorch-wheels/cu126/; \
    else \
        echo "Installing PyTorch CPU..." && \
        pip install --no-cache-dir torch==2.9.1 torchvision==0.24.1 \
            -f https://mirrors.aliyun.com/pytorch-wheels/cpu/; \
    fi

# 注意: PaddlePaddle 和 PaddleOCR 已移除
# OCR 功能通过外部 API 调用实现
# 配置方式:
#   1. 环境变量: OCR_API_URL=http://host.docker.internal:8000/v2/models/ocr/infer
#   2. docker-compose.yaml 中的 environment 配置
#   3. .env 文件

# 安装其他依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app.py .
COPY database.py .
COPY data/ ./data/
COPY config.yaml ./config.yaml
COPY ai_service/ ./ai_service/
COPY frontend/dist/ ./frontend/dist/

# 创建必要目录
RUN mkdir -p /app/images /app/labeled /app/data /app/models

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:5000/api/stats || exit 1

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:5000", \
     "--workers", "1", \
     "--threads", "4", \
     "--timeout", "600", \
     "--keep-alive", "5", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "app:app"]
