#!/bin/bash
# Install system binaries for infrastructure repo
# Run this script when setting up a new machine

set -e  # Exit on error

BIN_DIR="$HOME/infrastructure/system-utilities/bin"
mkdir -p "$BIN_DIR"

echo "Installing system binaries to $BIN_DIR..."

# Detect architecture
ARCH=$(uname -m)
OS=$(uname -s)

# ripgrep
echo "Installing ripgrep..."
if [ "$OS" = "Linux" ] && [ "$ARCH" = "x86_64" ]; then
    RG_VERSION="14.1.1"
    RG_URL="https://github.com/BurntSushi/ripgrep/releases/download/${RG_VERSION}/ripgrep-${RG_VERSION}-x86_64-unknown-linux-musl.tar.gz"

    curl -L "$RG_URL" -o /tmp/ripgrep.tar.gz
    tar -xzf /tmp/ripgrep.tar.gz -C /tmp
    cp /tmp/ripgrep-${RG_VERSION}-x86_64-unknown-linux-musl/rg "$BIN_DIR/rg"
    chmod +x "$BIN_DIR/rg"
    rm -rf /tmp/ripgrep.tar.gz /tmp/ripgrep-*
    echo "✓ ripgrep installed"
else
    echo "⚠ Unsupported platform for ripgrep: $OS $ARCH"
    echo "  Please install manually from https://github.com/BurntSushi/ripgrep"
fi

# yt-dlp
echo "Installing yt-dlp..."
if [ "$OS" = "Linux" ]; then
    YT_DLP_URL="https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp"

    curl -L "$YT_DLP_URL" -o "$BIN_DIR/yt-dlp"
    chmod +x "$BIN_DIR/yt-dlp"
    echo "✓ yt-dlp installed"
else
    echo "⚠ Unsupported platform for yt-dlp: $OS"
    echo "  Please install manually from https://github.com/yt-dlp/yt-dlp"
fi

echo ""
echo "Installation complete!"
echo "Binaries installed to: $BIN_DIR"
echo ""
echo "Make sure $BIN_DIR is in your PATH (already configured in ~/.bashrc from dotfiles)"
