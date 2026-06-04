"""
fb_reel_dl.downloader — core logic
───────────────────────────────────
Playwright-based infinite scroll to collect Facebook Reel URLs,
then yt-dlp to download them.
"""

import asyncio
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


# ── Config ─────────────────────────────────────────────────
SCROLL_STEPS = 200
SCROLL_WAIT = 3.0
PAGE_LOAD_WAIT = 6.0
BOTTOM_STALL_LIMIT = 5


# ── Helpers ────────────────────────────────────────────────

def log(msg: str, emoji: str = "ℹ️"):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"  {emoji} [{ts}] {msg}")


def clean_url(url: str) -> str:
    return url.split("?")[0].split("&")[0].rstrip("/")


def extract_reel_id(url: str) -> str | None:
    m = re.search(r"/reel/(\d+)", url)
    return m.group(1) if m else None


def load_cookies(path: str) -> list[dict]:
    ext = Path(path).suffix.lower()
    if ext != ".json":
        log("Only JSON cookie format supported", "⚠️")
        return []
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        log(f"Cookie error: {e}", "❌")
        return []


def get_channel_name(url: str, name_arg: str | None) -> str:
    if name_arg:
        return name_arg
    m = re.search(r"id=(\d+)", url)
    return f"profile_{m.group(1)}" if m else "facebook_reels"


# ── Collect URLs ───────────────────────────────────────────

async def collect_reel_urls(
    url: str,
    cookies_path: str | None = None,
    headless: bool = True,
    output_base: str = "downloads",
) -> list[str]:
    """Scroll Facebook reels_tab and collect all reel video URLs."""

    seen: set[str] = set()
    stall = 0
    start = time.time()

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
                log(f"Loaded {len(cookies)} cookies", "🍪")

        page = await context.new_page()

        # Block heavy resources
        await page.route(
            re.compile(r"\.(png|jpg|jpeg|gif|svg|woff2?|ttf|eot)($|\?)"),
            lambda route: route.abort(),
        )

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        except PWTimeoutError:
            log("Page load timeout — continuing", "⚠️")

        await page.wait_for_timeout(int(PAGE_LOAD_WAIT * 1000))

        # Dismiss popups
        for sel in [
            'div[aria-label="Close"]', 'div[aria-label="ปิด"]',
            'div[role="button"]:has-text("Not now")',
            'div[role="button"]:has-text("ไม่ใช่ตอนนี้")',
        ]:
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
            if await page.locator(
                "#loginform, form:has([name=email]), input[name=email]"
            ).first.is_visible(timeout=2000):
                log("Login required — use --visible or --cookies", "🔑")
        except Exception:
            pass

        # Infinite scroll
        log(f"Scrolling (max {SCROLL_STEPS})...", "📜")

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
            stall = 0 if delta else stall + 1

            print(
                f"  \r  [{i:3d}/{SCROLL_STEPS}] {len(seen):4d} reels"
                f"  {'+'+str(delta) if delta else '   '}"
                f"  {'🔄' if stall == 0 else f'⏳stall {stall}/{BOTTOM_STALL_LIMIT}'}",
                end="", flush=True,
            )

            if stall >= BOTTOM_STALL_LIMIT:
                print()
                log("Reached bottom", "✅")
                break

        print()
        elapsed = time.time() - start
        log(f"Found {len(seen)} reels in {elapsed:.0f}s", "📊")

        if not headless:
            await page.wait_for_timeout(2000)

        await browser.close()

    return sorted(seen, key=lambda u: extract_reel_id(u) or u)


# ── Download ───────────────────────────────────────────────

def download_reels(urls: list[str], channel: str, output_base: str = "downloads"):
    """Download reels with yt-dlp."""
    if not urls:
        log("No reels to download", "❌")
        return

    out_dir = os.path.join(output_base, channel)
    os.makedirs(out_dir, exist_ok=True)

    list_path = os.path.join(output_base, f"{channel}_urls.txt")
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
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            universal_newlines=True, bufsize=1,
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

    log(f"URL list: {list_path}", "📋")


def save_urls_only(urls: list[str], channel: str, output_base: str = "downloads"):
    """Save URLs without downloading."""
    out_dir = os.path.join(output_base, channel)
    os.makedirs(out_dir, exist_ok=True)

    list_path = os.path.join(output_base, f"{channel}_urls.txt")
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
