# ============================================
# PLC & Python 开发环境 Docker镜像
# 基于 Microsoft Dev Containers 官方基础镜像
# 支持环境：Python 3.11, Go 1.24, Siemens LSP
# ============================================

FROM mcr.microsoft.com/devcontainers/python:0-3.11-bullseye

# 避免交互式提示
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai

# 删除 Yarn 仓库配置（密钥已过期，导致构建失败）
RUN rm -rf /etc/apt/sources.list.d/*.list 2>/dev/null || true

# 配置国内 Debian 镜像源（加速下载）
RUN echo "deb http://mirrors.tuna.tsinghua.edu.cn/debian/ bullseye main contrib non-free" > /etc/apt/sources.list && \
    echo "deb http://mirrors.tuna.tsinghua.edu.cn/debian-security/ bullseye-security main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.tuna.tsinghua.edu.cn/debian/ bullseye-updates main contrib non-free" >> /etc/apt/sources.list

# 安装系统依赖包
RUN apt-get update && apt-get install -y \
    # ==================== Go语言环境 ====================
    golang-go \
    # ==================== GUI支持库（PyQt5需要）====================
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libx11-xcb1 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-xfixes0 \
    libxcb-xinerama0 \
    libxcb-xinput0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    # ==================== 中文支持 ====================
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    locales \
    # ==================== 常用开发工具 ====================
    curl \
    wget \
    vim \
    git \
    zip \
    unzip \
    ca-certificates \
    gnupg \
    lsb-release \
    # ==================== 构建工具 ====================
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 配置中文 locale 支持
RUN sed -i '/zh_CN.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen zh_CN.UTF-8 && \
    update-locale LANG=zh_CN.UTF-8

ENV LANG zh_CN.UTF-8
ENV LANGUAGE zh_CN:zh
ENV LC_ALL zh_CN.UTF-8

# 安装 Python 全局开发工具
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        pytest==8.0.1 \
        pytest-cov==4.1.0 \
        black==24.2.0 \
        flake8==7.0.0 \
        mypy==1.9.0 \
        isort==5.13.2

# 配置 Git 全局设置（可被挂载的 .gitconfig 覆盖）
RUN git config --global core.autocrlf input && \
    git config --global core.safecrlf warn && \
    git config --global init.defaultBranch main

# 创建常用目录结构
RUN mkdir -p /go/src /go/bin /workspace

# 设置环境变量
ENV PYTHONPATH=/workspace
ENV GOPATH=/go
ENV PATH="${GOPATH}/bin:${PATH}"

# 设置工作目录
WORKDIR /workspace

# 容器默认命令（保持容器运行）
CMD ["sleep", "infinity"]
