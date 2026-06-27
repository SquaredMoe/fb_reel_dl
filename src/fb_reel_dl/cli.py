"""
fb_reel_dl.cli — command-line entry point
─────────────────────────────────────────
"""
import asyncio
import sys

from . import __version__

# Import the core functions
from .downloader import (
    collect_reel_urls,
    download_reels,
    get_channel_name,
    save_urls_only,
)
from .cookies import get_browsers_list


def build_parser():
    from argparse import ArgumentParser, RawDescriptionHelpFormatter

    available_browsers = get_browsers_list()

    parser = ArgumentParser(
        prog="fb-reel-dl",
        description=(
            "Facebook Reels Bulk Downloader 📱\n"
            "Playwright + yt-dlp — ดาวน์โหลด Reels ทั้งหมดจาก Facebook Profile"
        ),
        formatter_class=RawDescriptionHelpFormatter,
        epilog=f"""\
Examples:
───────────────────────────────────────────
  fb-reel-dl "https://www.facebook.com/profile.php?id=123&sk=reels_tab"
  fb-reel-dl <url> --visible
  fb-reel-dl <url> --name my_channel
  fb-reel-dl <url> --dry-run
  fb-reel-dl <url> --cookies fb_cookies.json
  fb-reel-dl <url> --cookies-from-browser chrome
  fb-reel-dl <url> --cookies-from-browser firefox

Supported browsers: {', '.join(available_browsers)}
        """,
    )

    parser.add_argument("url", help="Facebook profile URL (ต้องมี ?sk=reels_tab)")
    parser.add_argument("--name", "-n", help="ชื่อ output folder (default: auto)")
    parser.add_argument("--cookies", "-c", metavar="FILE", help="path ไปยัง cookies JSON")
    parser.add_argument(
        "--cookies-from-browser", metavar="BROWSER",
        help=(
            f"ดึง cookies จาก browser โดยตรง (ไม่ต้อง export JSON) — "
            f"ตัวเลือก: {', '.join(available_browsers)}"
        ),
    )
    parser.add_argument(
        "--visible", "-v", action="store_true",
        help="แสดง browser UI (ใช้ login ด้วยตนเอง)",
    )
    parser.add_argument(
        "--dry-run", "-d", action="store_true",
        help="แค่เก็บ URLs ไม่ดาวน์โหลด",
    )
    parser.add_argument(
        "--output", "-o", default="downloads",
        help="output directory (default: downloads/)",
    )
    parser.add_argument(
        "--version", action="version", version=f"fb-reel-dl v{__version__}",
    )
    return parser


async def async_main():
    parser = build_parser()
    args = parser.parse_args()

    # Validate: can't use both --cookies and --cookies-from-browser
    if args.cookies and args.cookies_from_browser:
        print(
            "  ❌ Use either --cookies FILE or --cookies-from-browser BROWSER, "
            "not both.",
        )
        sys.exit(1)

    channel = get_channel_name(args.url, args.name)
    headless = not args.visible

    urls = await collect_reel_urls(
        url=args.url,
        cookies_path=args.cookies,
        cookies_from_browser=args.cookies_from_browser,
        headless=headless,
        output_base=args.output,
    )

    if not urls:
        print("\n  😕 No reels found.")
        print("  💡 Tips:")
        print("     • Use --visible to log in manually")
        print("     • Use --cookies with a logged-in session")
        print("     • Use --cookies-from-browser chrome/firefox/...")
        print("     • Verify the profile has reels")
        sys.exit(1)

    if args.dry_run:
        save_urls_only(urls, channel, output_base=args.output)
    else:
        download_reels(urls, channel, output_base=args.output)

    print("\n  🎉 All done!\n")


def main():
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\n\n  ⛔ Cancelled by user\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
