#!/bin/bash
ARG_FILE_PATH="${1-}"

VENV_DIR="$(mktemp -d)"
mkdir -p ./uv_cache
mkdir -p ./oh-my-opencode-cache/
echo "Creating temporary virtual environment at $VENV_DIR"
echo "Caching uv packages in ./uv_cache"

docker run --rm -it --network=host \
    -e http_proxy=${http_proxy} \
    -e https_proxy=${https_proxy} \
    -e all_proxy=${all_proxy} \
    -e no_proxy=${no_proxy} \
    -v "./opencode_config/:/home/developer/.config/opencode/" \
    -v "./opencode_share/auth.json:/home/developer/.local/share/opencode/auth.json" \
    -v "./dot_claude/:/home/developer/.claude/" \
    -v "./opencode_config/skill/:/home/developer/.claude/skills/" \
    -v "${ARG_FILE_PATH}:/workspace/" \
    -v "$VENV_DIR":/workspace/.venv \
    -v "./uv_cache:/home/developer/.cache/uv" \
    -v "./oh-my-opencode-cache/:/home/developer/.cache/oh-my-opencode/" \
    opencode:test 

echo "Removing temporary virtual environment at $VENV_DIR"

rm -rf "$VENV_DIR"