# This .zshrc is configured for the dev container environment.

# Ensure UTF-8 locale for proper non-ASCII input/output
export LANG=${LANG:-en_US.UTF-8}
export LC_ALL=${LC_ALL:-en_US.UTF-8}
export LC_CTYPE=${LC_CTYPE:-en_US.UTF-8}
export LANGUAGE=${LANGUAGE:-en_US:en}

# Oh My Zsh user configuration
export ZSH="/etc/ohmyzsh"
ZSH_THEME="ys-me"
plugins=(
  git
  zsh-autosuggestions
  zsh-syntax-highlighting
)

alias clauded="claude --dangerously-skip-permissions"

export PATH="$HOME/.local/bin:$PATH"
export PATH="$HOME/.bun/bin:$PATH"
source $ZSH/oh-my-zsh.sh
