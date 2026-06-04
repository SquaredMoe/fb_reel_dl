#!/usr/bin/env python3
"""
Facebook Reels Bulk Downloader
──────────────────────────────────────────
ใช้ Playwright + yt-dlp ดาวน์โหลด Reels ทั้งหมดจาก Facebook Profile
"""

__version__ = "1.0.0"
__author__ = "nanofatdog"

import asyncio
import argparse
import csv
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse, urlunparse
from datetime import datetime

from playwright.async_api import async_playwright, TimeoutError as PWTimeoutError


# ═══════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════

OUTPUT_BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
SCROLL_STEPS = 200           # max scroll attempts
SCROLL_WAIT = 3.0            # seconds between scrolls
PAGE_LOAD_WAIT = 6.0         # initial page load wait
BOTTOM_STALL_LIMIT = 5       # break after N scrolls with no new reels


# ═══════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════

def log(msg: str, emoji: str = "ℹ️"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"  {emoji} [{timestamp}] {msg}")


def clean_url(url: str) -> str:
    """Normalize reel URL — strip FB tracking params"""
    return url.split("?")[0].split("&")[0].rstrip("/")


def extract_reel_id(url: str) -> str | None:
    """Extract reel ID from /reel/XXXXXXXXX"""
    m = re.search(r"/reel/(\d+)", url)
    return m.group(1) if m else None


def load_cookies(path: str) -> list[dict]:
    """Load cookies from a Playwright-format JSON file."""
    ext = Path(path).suffix.lower()
    if ext not in (".json",):
        log("Netscape (.txt) cookies not supported yet — use JSON format", "⚠️")
        return []
    try:
        with open(path) as f:
            cookies = json.load(f)
        log(f"Loaded {len(cookies)} cookies from {path}", "🍪")
        return cookies
    except (json.JSONDecodeError, FileNotFoundError) as e:
        log(f"Cookie error: {e}", "❌")
        return []


def get_channel_name(url: str, name_arg: str | None) -> str:
    """Derive output directory name from URL or user-supplied name."""
    if name_arg:
        return name_arg
    m = re.search(r"id=(\d+)", url)
    if m:
        return f"profile_{m.group(1)}"
    # fallback: use domain + path hash
    return "facebook_reels"


# ═══════════════════════════════════════════════════════════
#  CORE — Collect reel URLs from FB profile page
# ═══════════════════════════════════════════════════════════

async def collect_reel_urls(
    url: str,
    cookies_path: str | None = None,
    headless: bool = True,
) -> list[str]:
    """
    Open Facebook profile → reels_tab, scroll infinite scroll,
    collect all /reel/XXXX URLs, return deduplicated sorted list.
    """

    seen: set[str] = set()
    stall = 0
    start_time = time.time()

    log(f"Opening: {url}", "🚀")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )

        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
            ),
        )

        if cookies_path:
            cookies = load_cookies(cookies_path)
            if cookies:
                await context.add_cookies(cookies)

        page = await context.new_page()

        # Block heavy resources for speed
        await page.route(
            re.compile(r"\.(png|jpg|jpeg|gif|svg|woff2?|ttf|eot)($|\?)"),
            lambda route: route.abort(),
        )

        # Navigate
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        except PWTimeoutError:
            log("Page load timeout — continuing anyway", "⚠️")

        await page.wait_for_timeout(int(PAGE_LOAD_WAIT * 1000))

        # ── Dismiss popups ──
        popup_selectors = [
            'div[aria-label="Close"]',
            'div[aria-label="ปิด"]',
            'div[role="button"]:has-text("Not now")',
            'div[role="button"]:has-text("ไม่ใช่ตอนนี้")',
            '[aria-label="Close"][role="button"]',
        ]
        for sel in popup_selectors:
            try:
                btn = page.locator(sel).first
                if await btn.is_visible(timeout=1500):
                    await btn.click()
                    await page.wait_for_timeout(800)
                    log("Dismissed popup", "✅")
                    break
            except Exception:
                continue

        # Detect login wall
        try:
            login_visible = await page.locator(
                "#loginform, form:has([name=email]), input[name=email]"
            ).first.is_visible(timeout=2000)
            if login_visible:
                log(
                    "Login required — use --visible to sign in manually, "
                    "or --cookies with a logged-in session",
                    "🔑",
                )
        except Exception:
            pass

        # ── Scroll & collect ──
        log(f"Scrolling (max {SCROLL_STEPS} passes)...", "📜")

        for i in range(1, SCROLL_STEPS + 1):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(int(SCROLL_WAIT * 1000))

            links = await page.evaluate(
                """() => Array.from(
                    document.querySelectorAll('a[href*="/reel/"]')
                ).map(a => a.href)"""
            )

            before = len(seen)
            for link in links:
                cleaned = clean_url(link)
                rid = extract_reel_id(cleaned)
                if rid:
                    seen.add(cleaned)

            delta = len(seen) - before
            if delta == 0:
                stall += 1
            else:
                stall = 0

            # Progress line
            bar = "█" * min(i % 50, 50)  # simple progress indicator
            print(
                f"  \r  [{i:3d}/{SCROLL_STEPS}] {len(seen):4d} reels"
                f"  {'+'+str(delta) if delta else '   '}"
                f"  {'🔄' if stall == 0 else f'⏳stall {stall}/{BOTTOM_STALL_LIMIT}'}",
                end="",
                flush=True,
            )

            if stall >= BOTTOM_STALL_LIMIT:
                print()
                log(f"Reached bottom — stopping", "✅")
                break

        print()
        elapsed = time.time() - start_time
        log(f"Found {len(seen)} reels in {elapsed:.0f}s", "📊")

        if not headless:
            await page.wait_for_timeout(2000)

        await browser.close()

    return sorted(seen, key=lambda u: extract_reel_id(u) or u)


# ═══════════════════════════════════════════════════════════
#  DOWNLOAD with yt-dlp
# ═══════════════════════════════════════════════════════════

def download_reels(urls: list[str], channel: str) -> None:
    """Download reels using yt-dlp."""
    if not urls:
        log("No reels to download", "❌")
        return

    out_dir = os.path.join(OUTPUT_BASE, channel)
    os.makedirs(out_dir, exist_ok=True)

    # Write URL list
    list_path = os.path.join(OUTPUT_BASE, f"{channel}_urls.txt")
    with open(list_path, "w") as f:
        for u in urls:
            f.write(u + "\n")

    log(f"Downloading {len(urls)} reels → {out_dir}/", "⬇️")

    cmd = [
        "yt-dlp",
        "-f", "best[ext=mp4]+bestaudio[ext=m4a]/best",
        "--limit-rate", "50M",
        "--concurrent-fragments", "4",
        "--retries", "10",
        "--no-warnings",
        "--progress",
        "-a", list_path,
        "--output", os.path.join(out_dir, "%(id)s.%(ext)s"),
    ]

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
        )
        for line in iter(proc.stdout.readline, ""):
            line = line.strip()
            if line and not line.startswith("[debug]"):
                print(f"  {line}")
        proc.wait()

        if proc.returncode == 0:
            log(f"Done! Files in {out_dir}/", "✅")
        else:
            log(f"yt-dlp exited with code {proc.returncode}", "⚠️")

    except FileNotFoundError:
        log("yt-dlp not found. Install: pip install yt-dlp", "❌")
        sys.exit(1)

    log(f"URL list saved: {list_path}", "📋")


def save_urls_only(urls: list[str], channel: str) -> None:
    """Save URLs without downloading."""
    out_dir = os.path.join(OUTPUT_BASE, channel)
    os.makedirs(out_dir, exist_ok=True)

    list_path = os.path.join(OUTPUT_BASE, f"{channel}_urls.txt")
    with open(list_path, "w") as f:
        for u in urls:
            f.write(u + "\n")

    csv_path = os.path.join(out_dir, "reels_list.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["reel_id", "url"])
        for u in urls:
            w.writerow([extract_reel_id(u), u])

    log(f"Saved {len(urls)} URLs to {list_path}", "📋")
    log(f"CSV → {csv_path}", "📊")


# ═══════════════════════════════════════════════════════════
#  CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════

async def main():
    parser = argparse.ArgumentParser(
        prog="fb_reel_dl",
        description="Facebook Reels Bulk Downloader 📱 — ใช้ Playwright + yt-dlp "
                    "ดาวน์โหลด Reels ทั้งหมดจาก Facebook Profile",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
ตัวอย่างการใช้งาน:
───────────────────────────────────────────
  # 1) ดาวน์โหลด reels ทั้งหมด (headless)
  fb_reel_dl "https://www.facebook.com/profile.php?id=123&sk=reels_tab"

  # 2) เห็น browser UI (login ด้วยตนเองได้)
  fb_reel_dl <url> --visible

  # 3) ระบุชื่อ output folder
  fb_reel_dl <url> --name my_channel

  # 4) แค่เก็บ URLs ยังไม่โหลด
  fb_reel_dl <url> --dry-run

  # 5) ใช้ cookies จาก Chrome ที่ login แล้ว
  fb_reel_dl <url> --cookies fb_cookies.json
        """,
    )

    parser.add_argument("url", help="Facebook profile URL (ต้องมี ?sk=reels_tab)")
    parser.add_argument("--name", "-n", help="ชื่อ output folder (default: auto)")
    parser.add_argument("--cookies", "-c", metavar="FILE", help="path ไปยัง cookies JSON")
    parser.add_argument("--visible", "-v", action="store_true", help="แสดง browser UI (ใช้ login ด้วยตนเอง)")
    parser.add_argument("--dry-run", "-d", action="store_true", help="แค่เก็บ URLs ไม่ดาวน์โหลด")
    parser.add_argument("--version", action="version", version=f"fb_reel_dl v{__version__}")

    args = parser.parse_args()

    channel = get_channel_name(args.url, args.name)
    headless = not args.visible

    # Collect
    urls = await collect_reel_urls(
        url=args.url,
        cookies_path=args.cookies,
        headless=headless,
    )

    if not urls:
        log("No reels found.", "😕")
        log("Tips:", "💡")
        log("  • Use --visible to log in manually")
        log("  • Use --cookies with a logged-in session")
        log("  • Verify the profile actually has reels")
        sys.exit(1)

    # Output
    if args.dry_run:
        save_urls_only(urls, channel)
    else:
        download_reels(urls, channel)

    log("All done! ✨", "🎉")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n")
        log("Cancelled by user", "⛔")
        sys.exit(1)
