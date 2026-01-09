mkdir -p download
wget https://github.com/ClementTsang/bottom/releases/download/0.10.2/bottom_0.10.2-1_amd64.deb -O download/bottom.deb
wget https://github.com/bootandy/dust/releases/download/v1.2.1/du-dust_1.2.1-1_amd64.deb -O download/du-dust.deb
wget https://github.com/zellij-org/zellij/releases/latest/download/zellij-x86_64-unknown-linux-musl.tar.gz -O download/zellij.tar.gz
wget https://github.com/sharkdp/fd/releases/download/v10.2.0/fd-musl_10.2.0_amd64.deb -O download/fd.deb
wget https://github.com/fastfetch-cli/fastfetch/releases/download/2.47.0/fastfetch-linux-amd64.deb -O download/fastfetch.deb
tar -xzvf  download/zellij.tar.gz -C download/ && rm download/zellij.tar.gz