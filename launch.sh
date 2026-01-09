docker run --rm -it --network=host \
    -v "./opencode_config/bun.lock:/home/developer/.config/opencode/bun.lock" \
    -v "./opencode_config/oh-my-opencode.json:/home/developer/.config/opencode/oh-my-opencode.json" \
    -v "./opencode_config/opencode.json:/home/developer/.config/opencode/opencode.json" \
    -v "./opencode_config/packages.json:/home/developer/.config/opencode/packages.json" \
    -v "./opencode_config/.gitignore:/home/developer/.config/opencode/.gitignore" \
    -v "./opencode_share/auth.json:/home/developer/.local/share/opencode/auth.json" \
    opencode:test 

