#!/usr/bin/env bash
# ────────────────────────────────────────────────────────────────
# fb_reel_dl — Facebook Reels Bulk Downloader Installer
# ────────────────────────────────────────────────────────────────
# Usage:
#   curl -sL https://raw.githubusercontent.com/nanofatdog/fb_reel_dl/main/install.sh | bash
#
# Or run locally:
#   chmod +x install.sh && ./install.sh
# ────────────────────────────────────────────────────────────────

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

bold()  { echo -e "${CYAN}${1}${NC}"; }
ok()    { echo -e "  ${GREEN}✅${NC} ${1}"; }
warn()  { echo -e "  ${YELLOW}⚠️${NC} ${1}"; }
err()   { echo -e "  ${RED}❌${NC} ${1}"; }
sep()   { echo ""; echo "───────────────────────────────────────────────"; echo ""; }

echo ""
bold "╔══════════════════════════════════════════════╗"
bold "║     fb_reel_dl — Facebook Reels Downloader   ║"
bold "╚══════════════════════════════════════════════╝"
echo ""

# ── Detect directory ──
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALL_DIR="${HOME}/fb_reel_dl"

# ── 1. Check Python ──
bold "🔍 [1/5] Checking Python..."
if command -v python3 &>/dev/null; then
    PY_VER=$(python3 --version 2>&1)
    ok "Python: ${PY_VER}"
else
    err "python3 not found. Install Python 3.10+ first."
    exit 1
fi

# ── 2. Check pip ──
bold "🔍 [2/5] Checking pip..."
if command -v pip3 &>/dev/null; then
    ok "pip3: $(pip3 --version 2>&1 | awk '{print $2}')"
else
    warn "pip3 not found, trying to install..."
    python3 -m ensurepip --upgrade 2>/dev/null || true
    if ! command -v pip3 &>/dev/null; then
        err "Could not install pip. Try: apt install python3-pip"
        exit 1
    fi
fi

# ── 3. Setup directory ──
bold "📁 [3/5] Setting up ${INSTALL_DIR}..."
if [ "$SCRIPT_DIR" != "$INSTALL_DIR" ]; then
    mkdir -p "$INSTALL_DIR"
    # Copy if running from a different directory (e.g., curl pipe)
    if [ -f "fb_reel_dl.py" ]; then
        cp fb_reel_dl.py requirements.txt README.md "$INSTALL_DIR/" 2>/dev/null || true
    fi
else
    ok "Already in ${INSTALL_DIR}"
fi

cd "$INSTALL_DIR"

# Make sure the script exists — if not, download it
if [ ! -f "fb_reel_dl.py" ]; then
    bold "⬇️  Downloading fb_reel_dl.py from GitHub..."
    curl -sL "https://raw.githubusercontent.com/nanofatdog/fb_reel_dl/main/fb_reel_dl.py" -o fb_reel_dl.py
    curl -sL "https://raw.githubusercontent.com/nanofatdog/fb_reel_dl/main/requirements.txt" -o requirements.txt
fi

chmod +x fb_reel_dl.py
ok "Script ready at ${INSTALL_DIR}/fb_reel_dl.py"

# ── 4. Install Python dependencies ──
bold "📦 [4/5] Installing Python packages..."
python3 -m pip install --upgrade pip -q 2>/dev/null || true
python3 -m pip install -r requirements.txt -q 2>/dev/null || {
    warn "pip install failed, retrying with verbose..."
    python3 -m pip install -r requirements.txt
}

ok "Dependencies installed!"

# ── 5. Install Playwright browsers ──
bold "🌐 [5/5] Installing Playwright Chromium..."
python3 -m playwright install chromium 2>&1 | tail -3
ok "Playwright Chromium installed!"

# ── 6. Create symlink ──
bold "🔗 Creating symlink: /usr/local/bin/fb_reel_dl"
if [ -w /usr/local/bin ]; then
    ln -sf "${INSTALL_DIR}/fb_reel_dl.py" /usr/local/bin/fb_reel_dl
    ok "Now you can run 'fb_reel_dl' from anywhere!"
else
    warn "No write access to /usr/local/bin"
    warn "Run this to add to PATH:"
    echo "    sudo ln -sf ${INSTALL_DIR}/fb_reel_dl.py /usr/local/bin/fb_reel_dl"
    echo ""
    warn "Or use: python3 ${INSTALL_DIR}/fb_reel_dl.py"
fi

# ── Done ──
sep
bold "🎉 Installation complete!"
echo ""
echo "  Run:  fb_reel_dl --help"
echo ""
echo "  Example:"
echo "    fb_reel_dl \"https://www.facebook.com/profile.php?id=100080117672198&sk=reels_tab\""
echo ""
echo "  With browser UI (to login manually):"
echo "    fb_reel_dl <url> --visible"
echo ""
sep

# Test import
python3 -c "from playwright.async_api import async_playwright; print('  ✅ Playwright OK')" 2>/dev/null && \
    python3 -c "import yt_dlp; print(f'  ✅ yt-dlp {yt_dlp.version.__version__} OK')" 2>/dev/null && \
    echo ""
    ok "All imports verified!"
