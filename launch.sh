#!/bin/bash
ARG_FILE_PATH="${1-}"

VENV_DIR="$(mktemp -d)"
mkdir -p ./uv_cache

echo "Creating temporary virtual environment at $VENV_DIR"
echo "Caching uv packages in ./uv_cache"

docker run --rm -it --network=host \
    -v "./opencode_config/bun.lock:/home/developer/.config/opencode/bun.lock" \
    -v "./opencode_config/oh-my-opencode.json:/home/developer/.config/opencode/oh-my-opencode.json" \
    -v "./opencode_config/opencode.json:/home/developer/.config/opencode/opencode.json" \
    -v "./opencode_config/packages.json:/home/developer/.config/opencode/packages.json" \
    -v "./opencode_config/.gitignore:/home/developer/.config/opencode/.gitignore" \
    -v "./opencode_config/skill/:/home/developer/.config/opencode/skill/" \
    -v "./opencode_share/auth.json:/home/developer/.local/share/opencode/auth.json" \
    -v "${ARG_FILE_PATH}:/workspace/" \
    -v "$VENV_DIR":/workspace/.venv \
    -v "./uv_cache:/home/developer/.cache/uv" \
    opencode:test 

echo "Removing temporary virtual environment at $VENV_DIR"

rm -rf "$VENV_DIR"
