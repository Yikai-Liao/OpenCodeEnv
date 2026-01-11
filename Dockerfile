FROM astral/uv:python3.12-bookworm-slim

ARG DEV_UID=1000
ARG DEV_GID=1000

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    LC_CTYPE=en_US.UTF-8 \
    LANGUAGE=en_US:en

# 先拷贝本地 deb
COPY download/ /tmp/download/

RUN printf '%s\n' \
  'deb http://mirrors.aliyun.com/debian bookworm main' \
  'deb http://mirrors.aliyun.com/debian bookworm-updates main' \
  'deb http://mirrors.aliyun.com/debian-security bookworm-security main' \
  > /etc/apt/sources.list

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gnupg \
    && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    sudo \
    wget \
    unzip \
    zstd \
    zsh \
    axel \
    git \
    git-lfs \
    gocryptfs \
    locales \
    tzdata \
    build-essential \
    cmake \
    gcc \
    g++ \
    clang \
    ninja-build \
    lsd \
    vim \
    bat \
    htop \
    mtr \
    net-tools \
    traceroute \
    iputils-ping \
    iputils-tracepath \
    iputils-arping \
    nodejs \
    && \
    sed -i 's/^# *\(en_US.UTF-8\) UTF-8/\1 UTF-8/' /etc/locale.gen && \
    sed -i 's/^# *\(zh_CN.UTF-8\) UTF-8/\1 UTF-8/' /etc/locale.gen && \
    locale-gen && \
    update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 && \
    if [ -n "$(ls -A /tmp/download/*.deb 2>/dev/null)" ]; then \
        dpkg -i /tmp/download/*.deb || apt-get -f install -y; \
    fi && \
    rm -rf /tmp/download && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Oh My Zsh（装到 /etc，避免污染用户 HOME）
RUN echo "Installing Oh My Zsh..." \
    && git clone --depth=1 https://github.com/ohmyzsh/ohmyzsh.git /etc/ohmyzsh \
    && git clone --depth=1 https://github.com/zsh-users/zsh-autosuggestions /etc/ohmyzsh/custom/plugins/zsh-autosuggestions \
    && git clone --depth=1 https://github.com/zsh-users/zsh-syntax-highlighting.git /etc/ohmyzsh/custom/plugins/zsh-syntax-highlighting \
    && chmod -R 755 /etc/ohmyzsh

COPY ys-me.zsh-theme /etc/ohmyzsh/themes/ys-me.zsh-theme

# ✅ 关键：用 build-arg 对齐宿主机 UID/GID 创建 developer
RUN set -eux; \
    if ! getent group "${DEV_GID}" >/dev/null; then groupadd -g "${DEV_GID}" developer; fi; \
    useradd -m -u "${DEV_UID}" -g "${DEV_GID}" -s /bin/zsh developer; \
    mkdir -p /workspace; \
    chown -R "${DEV_UID}:${DEV_GID}" /workspace /home/developer; \
    mkdir -p /home/developer/.cache /home/developer/.config /home/developer/.local/share; \
    chown -R "${DEV_UID}:${DEV_GID}" /home/developer

RUN printf "registry=https://registry.npmmirror.com/\n" > /etc/npmrc

USER developer
WORKDIR /workspace

COPY --chown=developer:developer zshrc /home/developer/.zshrc

RUN curl -fsSL https://bun.sh/install | bash
RUN printf '[install]\nregistry = "https://registry.npmmirror.com"\n' > /home/developer/.bunfig.toml
RUN /home/developer/.bun/bin/bun install -g opencode-ai
RUN /home/developer/.bun/bin/bun install -g @anthropic-ai/claude-code

RUN mkdir -p /home/developer/.local/share/opencode \
    && mkdir -p /home/developer/.config/opencode

ENV UV_TOOL_BIN_DIR=/home/developer/.local/bin
ENV UV_TOOL_DIR=/home/developer/.local/share/uv/tools
ENV UV_CACHE_DIR=/home/developer/.cache/uv
ENV XDG_BIN_HOME=/home/developer/.local/bin
ENV XDG_DATA_HOME=/home/developer/.local/share
ENV UV_DEFAULT_INDEX=https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple

COPY --chown=developer:developer 3rdparty/mat_preview /home/developer/tmp/mat_preview
RUN mkdir -p /home/developer/.local/bin /home/developer/.local/share \
    && mkdir -p /home/developer/.config/opencode \
    && mkdir -p /home/developer/.claude \
    && uv tool install /home/developer/tmp/mat_preview \
    && rm -rf /home/developer/tmp/mat_preview \
    && uv tool install "markitdown[all]"

COPY --chown=developer:developer 3rdparty/stimkit_gallery /stimkit_gallery
COPY --chown=developer:developer 3rdparty/stimkit /stimkit

CMD ["/bin/zsh"]
