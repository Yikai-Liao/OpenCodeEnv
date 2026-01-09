FROM astral/uv:python3.12-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
# Ensure UTF-8 locale inside container
ENV LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    LC_CTYPE=en_US.UTF-8 \
    LANGUAGE=en_US:en

# --- Stage 1: Root-level setup ---

# 1. Copy local packages FIRST so they are available for installation
# (Moved this up from the bottom to fix the "file not found" error)
COPY download/ /tmp/download/

# 2. System update, Tools, Node.js, and Bun installation
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gnupg \
    && \
    # Setup NodeSource repository (Node.js 20 LTS) - Provides nodejs and npm
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get update && \
    apt-get install -y \
    # Core utilities
    sudo \
    wget \
    unzip \
    zstd \
    zsh \
    axel \
    git-lfs \
    gocryptfs \
    locales \
    tzdata \
    # Build tools
    build-essential \
    cmake \
    gcc \
    g++ \
    clang \
    ninja-build \
    # Monitoring and viewing tools
    lsd \
    vim \
    bat \
    htop \
    # Network tools
    mtr \
    net-tools \
    traceroute \
    iputils-ping \
    iputils-tracepath \
    iputils-arping \
    # Node.js & npm (from NodeSource)
    nodejs \
    && \
    # Locale generation
    sed -i 's/^# *\(en_US.UTF-8\) UTF-8/\1 UTF-8/' /etc/locale.gen && \
    sed -i 's/^# *\(zh_CN.UTF-8\) UTF-8/\1 UTF-8/' /etc/locale.gen && \
    locale-gen && \
    update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 && \
    # Install local .deb packages
    # (Using shell check to avoid failure if directory is empty)
    if [ -n "$(ls -A /tmp/download/*.deb 2>/dev/null)" ]; then \
        dpkg -i /tmp/download/*.deb; \
    fi && \
    # Clean up
    rm -rf /tmp/download && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 3. Zellij Setup (Assuming zellij binary was in the download folder or handled separately)
# If zellij was a .deb, it's handled above. If it's a binary:
# RUN cp /tmp/download/zellij /usr/bin/zellij && chmod 755 /usr/bin/zellij
# (Commented out as specific zellij source path logic depends on your 'download' folder structure)

# 4. Zsh and Theme Setup
RUN echo "Installing Oh My Zsh..." \
    && git clone --depth=1 https://github.com/ohmyzsh/ohmyzsh.git /etc/ohmyzsh \
    && git clone --depth=1 https://github.com/zsh-users/zsh-autosuggestions /etc/ohmyzsh/custom/plugins/zsh-autosuggestions \
    && git clone --depth=1 https://github.com/zsh-users/zsh-syntax-highlighting.git /etc/ohmyzsh/custom/plugins/zsh-syntax-highlighting \
    && chmod -R 755 /etc/ohmyzsh

COPY ys-me.zsh-theme /etc/ohmyzsh/themes/ys-me.zsh-theme

# 5. User Creation
RUN useradd -m -s /bin/zsh developer \
    && mkdir -p /workspace \
    && chown developer:developer /workspace

# Switch to user
USER developer
WORKDIR /workspace
COPY zshrc /home/developer/.zshrc

RUN curl -fsSL https://bun.sh/install | bash 
RUN /home/developer/.bun/bin/bun install -g opencode-ai
RUN mkdir -p /home/developer/.local/share/opencode && mkdir -p /home/developer/.config/opencode

# Add Tool
COPY 3rdparty/mat_preview /home/developer/tmp/mat_preview
RUN uv tool install /home/developer/tmp/mat_preview \
    && rm -rf /home/developer/tmp/mat_preview \
    && uv tool install "markitdown[all]"

# Default command
CMD ["/bin/zsh"]