"""
fb_reel_dl.cookies — browser cookie extraction
───────────────────────────────────────────────
Extract Facebook cookies from installed browsers using browser-cookie3,
compatible with Playwright's add_cookies() format.

Usage:
    cookies = extract_cookies_from_browser("chrome")
    # returns list[dict] for Playwright context.add_cookies()
"""

from http.cookiejar import Cookie


# ── Browser name → function mapping ────────────────────────

def _get_browser_map():
    """
    Lazy import browser_cookie3 to avoid crash if not installed.
    Returns dict of {browser_name: loader_function} or None if unavailable.
    """
    try:
        import browser_cookie3 as bc3
    except ImportError:
        return None

    return {
        "chrome": bc3.chrome,
        "chromium": bc3.chromium,
        "firefox": bc3.firefox,
        "brave": bc3.brave,
        "edge": bc3.edge,
        "opera": bc3.opera,
        "opera_gx": bc3.opera_gx,
        "vivaldi": bc3.vivaldi,
        "arc": bc3.arc,
        "librewolf": bc3.librewolf,
        "safari": bc3.safari,
    }


def get_browsers_list() -> list[str]:
    """Return list of supported browser names."""
    bmap = _get_browser_map()
    if bmap is None:
        return []
    return sorted(bmap.keys())


def is_browser_cookie3_available() -> bool:
    """Check if browser-cookie3 is installed."""
    return _get_browser_map() is not None


# ── Conversion ─────────────────────────────────────────────

def _cookie_to_playwright(c: Cookie) -> dict:
    """Convert a http.cookiejar.Cookie to Playwright add_cookies() format."""
    # Playwright expects domain without leading dot
    domain = c.domain
    if domain and domain.startswith("."):
        domain = domain.lstrip(".")

    pw_cookie: dict = {
        "name": c.name,
        "value": c.value,
        "domain": domain or ".facebook.com",
        "path": c.path or "/",
        "secure": bool(c.secure),
        "httpOnly": False,
        "sameSite": "Lax",
    }

    # Detect HttpOnly from internal _rest dict (case-insensitive)
    if hasattr(c, "_rest") and c._rest:
        for key in c._rest:
            if key.lower() == "httponly":
                pw_cookie["httpOnly"] = True
                break

    if c.expires and c.expires != 0:
        pw_cookie["expires"] = float(c.expires)

    return pw_cookie


# ── Public API ─────────────────────────────────────────────

def extract_cookies_from_browser(
    browser_name: str,
    *,
    log_fn=print,
) -> list[dict]:
    """
    Extract Facebook cookies from an installed browser.

    Args:
        browser_name: One of chrome, chromium, firefox, brave, edge,
                     opera, opera_gx, vivaldi, arc, librewolf, safari.
        log_fn:      Callback for status messages (default: print).

    Returns:
        List of cookie dicts compatible with Playwright's add_cookies().
        Empty list on failure.
    """
    bmap = _get_browser_map()

    if bmap is None:
        log_fn(
            "  ❌ [cookies] browser-cookie3 not installed. "
            "Install: pip install browser-cookie3"
        )
        return []

    if browser_name not in bmap:
        browsers = ", ".join(sorted(bmap.keys()))
        log_fn(
            f"  ❌ [cookies] Unknown browser: '{browser_name}'. "
            f"Supported: {browsers}"
        )
        return []

    log_fn(f"  🔍 [cookies] Extracting Facebook cookies from {browser_name}...")

    try:
        # Get cookies for facebook.com domain
        cj = bmap[browser_name](domain_name="facebook.com")
    except Exception as e:
        log_fn(
            f"  ⚠️ [cookies] {browser_name} extraction failed: {e}\n"
            f"  💡 Make sure you're logged into Facebook in {browser_name} "
            f"and it has a profile with cookies."
        )
        return []

    playwright_cookies = []
    for c in cj:
        if not c.value:
            continue
        try:
            pw_c = _cookie_to_playwright(c)
            playwright_cookies.append(pw_c)
        except Exception:
            continue  # skip malformed cookies

    if playwright_cookies:
        log_fn(
            f"  🍪 [cookies] Got {len(playwright_cookies)} cookies "
            f"from {browser_name}"
        )
    else:
        log_fn(
            f"  😕 [cookies] No Facebook cookies found in {browser_name}. "
            f"Try logging into Facebook first."
        )

    return playwright_cookies
