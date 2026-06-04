#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
# fb-reel-dl — Facebook Reels Bulk Downloader Installer
# ──────────────────────────────────────────────────────────────
# วิธีใช้:
#   curl -sL https://raw.githubusercontent.com/nanofatdog/fb_reel_dl/main/install.sh | bash
#
# หรือ:
#   pip install fb-reel-dl
#   playwright install chromium
# ──────────────────────────────────────────────────────────────

set -e

RED='\033[0;31m'; GREEN='\033[0;32m'
YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
bold() { echo -e "${CYAN}${1}${NC}"; }
ok()   { echo -e "  ${GREEN}✅${NC} ${1}"; }
warn() { echo -e "  ${YELLOW}⚠️${NC} ${1}"; }
err()  { echo -e "  ${RED}❌${NC} ${1}"; }

echo ""
bold "╔══════════════════════════════════════════════╗"
bold "║     fb-reel-dl — Facebook Reels Downloader  ║"
bold "╚══════════════════════════════════════════════╝"
echo ""

# ── 1. Check Python ──
bold "🔍 [1/5] Checking Python..."
if command -v python3 &>/dev/null; then
    ok "Python: $(python3 --version 2>&1)"
else
    err "python3 not found. Install Python 3.10+ first."
    exit 1
fi

# ── 2. Check pip ──
bold "🔍 [2/5] Checking pip..."
if command -v pip3 &>/dev/null; then
    ok "pip3: $(pip3 --version 2>&1 | awk '{print $2}')"
else
    python3 -m ensurepip --upgrade 2>/dev/null || true
fi

# ── 3. Install via pip ──
bold "📦 [3/5] Installing fb-reel-dl..."
INSTALL_MODE="pip"

# ถ้ามี git clone อยู่แล้ว ให้ install แบบ local
if [ -f "pyproject.toml" ] && [ -d "src/fb_reel_dl" ]; then
    pip install -e . -q 2>/dev/null
    ok "Installed from local source (editable mode)"
    INSTALL_MODE="local"
else
    # Install จาก PyPI หรือ GitHub
    if pip install fb-reel-dl -q 2>/dev/null; then
        ok "Installed from PyPI"
    else
        warn "PyPI not available yet — installing from GitHub..."
        pip install git+https://github.com/nanofatdog/fb_reel_dl.git -q
        ok "Installed from GitHub"
    fi
fi

# ── 4. Install Playwright browser ──
bold "🌐 [4/5] Installing Playwright Chromium..."
python3 -m playwright install chromium 2>&1 | tail -1
ok "Playwright Chromium ready!"

# ── 5. Verify ──
bold "🔍 [5/5] Verifying installation..."
if command -v fb-reel-dl &>/dev/null; then
    ok "$(fb-reel-dl --version 2>&1)"
else
    warn "Command 'fb-reel-dl' not in PATH. Using python3 -m fb_reel_dl"
fi

# Test imports
python3 -c "
from playwright.async_api import async_playwright
import yt_dlp
print(f'  ✅ yt-dlp {yt_dlp.version.__version__}')
print(f'  ✅ Playwright OK')
print(f'  ✅ fb-reel-dl ready!')
" 2>/dev/null

echo ""
bold "🎉 Installation complete!"
echo ""
echo "  Run:  fb-reel-dl --help"
echo ""
echo "  Example:"
echo "    fb-reel-dl \"https://www.facebook.com/your-profile/reels_tab\""
echo ""
echo "  With browser UI (to log in manually):"
echo "    fb-reel-dl <url> --visible"
echo ""
