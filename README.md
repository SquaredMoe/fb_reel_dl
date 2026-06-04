# fb_reel_dl 📱

> **Facebook Reels Bulk Downloader** — Download all Facebook Reels from a profile
> using Playwright + yt-dlp (automated scroll + batch download)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎯 **Bulk download** | Infinite scroll to collect all reel URLs → batch download |
| 🕵️ **Headless mode** | Run without visible browser (default) |
| 👁️ **Visible mode** | Show browser UI — log in manually if needed |
| 🍪 **Cookie support** | Load cookies from JSON — no repeated login |
| 📋 **Dry-run mode** | Collect URLs only, skip video download |
| 📊 **CSV export** | Save reel_id + URL as CSV |
| 🧹 **Auto-cleanup** | Strip tracking params, deduplicate by reel ID |
| 🚀 **yt-dlp backend** | High-speed, resume support, retry logic |

---

## 🔧 Installation

### Option 1: pip install (recommended) 🐍

```bash
pip install fb-reel-dl
playwright install chromium
```

Then use `fb-reel-dl` directly:

```bash
fb-reel-dl "https://www.facebook.com/your-profile/reels_tab"
```

### Option 2: pip from GitHub

```bash
pip install git+https://github.com/nanofatdog/fb_reel_dl.git
playwright install chromium
```

### Option 3: One-liner (curl → bash) 🚀

```bash
curl -sL https://raw.githubusercontent.com/nanofatdog/fb_reel_dl/main/install.sh | bash
```

### Option 4: Manual clone

```bash
git clone https://github.com/nanofatdog/fb_reel_dl.git
cd fb_reel_dl
pip install -r requirements.txt
playwright install chromium
python fb_reel_dl.py --help
```

---

## 📖 Usage

### 🎬 Download all reels (headless)

```bash
fb-reel-dl "https://www.facebook.com/your-profile/reels_tab"
```

Or using Python module:
```bash
python -m fb_reel_dl "https://www.facebook.com/your-profile/reels_tab"
```

### 👁️ Show browser UI (log in manually)

```bash
fb-reel-dl <url> --visible
```

When browser opens:
1. Log in to Facebook (if not already logged in)
2. The script will automatically scroll to collect reels
3. Press Ctrl+C to stop at any time

### 🍪 Use cookies (skip login)

Export cookies from a browser extension like [Cookie-Editor](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm) → Export → JSON:

```bash
fb-reel-dl <url> --cookies fb_cookies.json
```

### 📋 Dry-run (URLs only, no download)

```bash
fb-reel-dl <url> --dry-run
```

Output files:
- `downloads/<channel>/reels_list.csv` — reel_id + URL
- `downloads/<channel>_urls.txt` — plain URLs

### 🏷️ Custom output folder

```bash
fb-reel-dl <url> --name my_channel
```

### 📂 Custom output directory

```bash
fb-reel-dl <url> --output ./my_videos
```

---

## 📂 Output structure

```
fb_reel_dl/
├── fb_reel_dl.py          # main script
├── requirements.txt
├── README.md
├── install.sh
└── downloads/
    └── <channel_name>/     # change with --name
        ├── reel_12345.mp4
        ├── reel_67890.mp4
        └── ...
    └── <channel_name>_urls.txt   # URL list
```

---

## ⚙️ How it works

```
┌─────────────────────────────────────────────────────────────────┐
│  1. Playwright launches Chromium                               │
│     → Opens Facebook profile ?sk=reels_tab                     │
│                                                                │
│  2. Handle popups / login                                       │
│     → Dismiss popups, wait for page load                        │
│                                                                │
│  3. Infinite scroll (up to 200 passes)                          │
│     → Collect every <a href="/reel/XXXX">                      │
│     → Strip tracking params, deduplicate by reel ID             │
│                                                                │
│  4. Auto-stop after 5 scrolls with no new reels                 │
│                                                                │
│  5. Feed URL list to yt-dlp                                     │
│     → yt-dlp downloads MP4 to downloads/<channel>/              │
│                                                                │
│  6. Done! 🎉                                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔑 Exporting cookies (for --cookies)

Best for: log in once, export cookies, reuse without logging in again.

1. Install [Cookie-Editor](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm) extension
2. Go to [facebook.com](https://facebook.com) and log in
3. Click Cookie-Editor icon → Export → JSON
4. Save as `fb_cookies.json`
5. Run:

```bash
fb-reel-dl "https://www.facebook.com/your-profile/reels_tab" --cookies fb_cookies.json
```

---

## 🚨 Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `SessionNotCreatedException` | Chrome/Chromium not installed | `playwright install chromium` |
| No reels found | Not logged in | Use `--visible` or `--cookies` |
| Popup not dismissed | FB UI changed | Use `--visible` to handle manually |
| yt-dlp error | Not installed correctly | `pip install -U yt-dlp` |
| `ModuleNotFoundError` | Missing dependency | `pip install -r requirements.txt` |

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| [playwright](https://playwright.dev/) | >= 1.40 | Browser automation (scroll, collect URLs) |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | >= 2024 | Video download engine |

---

## 📝 License

MIT © [nanofatdog](https://github.com/nanofatdog)

---

## 🙏 Credits

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — best community downloader
- [Playwright](https://playwright.dev/) — Microsoft's browser automation
- [duongxthanh/facebook-reels-downloader](https://github.com/duongxthanh/facebook-reels-downloader) — inspiration

---

---

# fb_reel_dl 📱 (ภาษาไทย)

> **Facebook Reels Bulk Downloader** — ดาวน์โหลด Reels ทั้งหมดจาก Facebook Profile
> ด้วย Playwright + yt-dlp แบบอัตโนมัติ

---

## ✨ ความสามารถ

| Feature | รายละเอียด |
|---------|------------|
| 🎯 **โหลดทีละมากๆ** | Scroll อัตโนมัติ เก็บ reel URLs ทั้งหมด → ดาวน์โหลด |
| 🕵️ **Headless mode** | รันแบบไม่เห็น browser (ค่าเริ่มต้น) |
| 👁️ **Visible mode** | เห็น browser UI — ใช้ login ด้วยตนเองได้ |
| 🍪 **รองรับ Cookies** | ใช้ cookies JSON — ไม่ต้อง login ทุกครั้ง |
| 📋 **Dry-run mode** | แค่เก็บ URL list, ยังไม่โหลดวิดีโอ |
| 📊 **CSV export** | บันทึก reel_id + URL เป็น CSV |
| 🧹 **Auto-cleanup** | ตัด tracking params, deduplicate reel URLs |
| 🚀 **yt-dlp backend** | ความเร็วสูง, รองรับ resume, retry |

---

## 🔧 วิธีติดตั้ง

### วิธีที่ 1: pip install (แนะนำ!) 🐍

```bash
pip install fb-reel-dl
playwright install chromium
```

จากนั้นใช้คำสั่ง `fb-reel-dl` ได้เลย!

```bash
fb-reel-dl "https://www.facebook.com/your-profile/reels_tab"
```

### วิธีที่ 2: pip จาก GitHub

```bash
pip install git+https://github.com/nanofatdog/fb_reel_dl.git
playwright install chromium
```

### วิธีที่ 3: One-liner (curl → bash) 🚀

```bash
curl -sL https://raw.githubusercontent.com/nanofatdog/fb_reel_dl/main/install.sh | bash
```

### วิธีที่ 4: Clone ด้วยตนเอง

```bash
git clone https://github.com/nanofatdog/fb_reel_dl.git
cd fb_reel_dl
pip install -r requirements.txt
playwright install chromium
python fb_reel_dl.py --help
```

---

## 📖 วิธีใช้

### 🎬 ดาวน์โหลด reels ทั้งหมด (headless)

```bash
fb-reel-dl "https://www.facebook.com/your-profile/reels_tab"
```

หรือใช้ python module:
```bash
python -m fb_reel_dl "https://www.facebook.com/your-profile/reels_tab"
```

### 👁️ เห็น browser UI (login ด้วยตนเอง)

```bash
fb-reel-dl <url> --visible
```

พอ browser เปิดขึ้นมา:
1. Login Facebook (ถ้ายังไม่ login)
2. สคริปต์จะ scroll เก็บ reels ให้อัตโนมัติ
3. กด Ctrl+C เพื่อหยุดได้ทุกเมื่อ

### 🍪 ใช้ cookies (ไม่ต้อง login ทุกครั้ง)

Export cookies จาก browser extension เช่น [Cookie-Editor](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)
→ Export → JSON → แล้วใช้:

```bash
fb-reel-dl <url> --cookies fb_cookies.json
```

### 📋 แค่เก็บ URLs (ไม่โหลด)

```bash
fb-reel-dl <url> --dry-run
```

ได้ไฟล์:
- `downloads/<channel>/reels_list.csv` — reel_id + URL
- `downloads/<channel>_urls.txt` — plain URLs

### 🏷️ กำหนดชื่อ output folder

```bash
fb-reel-dl <url> --name my_channel
```

### 📂 กำหนด output directory

```bash
fb-reel-dl <url> --output ./my_videos
```

---

## 📂 โครงสร้างไฟล์

```
fb_reel_dl/
├── fb_reel_dl.py          # main script
├── requirements.txt
├── README.md
├── install.sh
└── downloads/
    └── <channel_name>/     # เปลี่ยนได้ด้วย --name
        ├── reel_12345.mp4
        ├── reel_67890.mp4
        └── ...
    └── <channel_name>_urls.txt   # URL list
```

---

## ⚙️ วิธีการทำงาน

```
┌─────────────────────────────────────────────────────────────────┐
│  1. Playwright เปิด Chromium                                     │
│     → โหลดหน้า Facebook Profile ?sk=reels_tab                   │
│                                                                  │
│  2. จัดการ popup/login                                           │
│     → ปิด popup, รอให้หน้าโหลด                                   │
│                                                                  │
│  3. Scroll infinite scroll (max 200 ครั้ง)                       │
│     → เก็บทุก <a href="/reel/XXXX">                              │
│     → ตัด tracking params, deduplicate ด้วย reel ID              │
│                                                                  │
│  4. ถ้า scroll 5 ครั้งติดไม่มี reel ใหม่ → หยุด                  │
│                                                                  │
│  5. ส่ง URL list ให้ yt-dlp                                      │
│     → yt-dlp ดาวน์โหลด MP4 ลง downloads/<channel>/              │
│                                                                  │
│  6. เสร็จ! 🎉                                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔑 การ export cookies (สำหรับ --cookies)

เหมาะสำหรับ: ใช้ครั้งเดียว login แล้ว export cookies → ใช้ซ้ำไม่ต้อง login อีก

1. ติดตั้ง extension [Cookie-Editor](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)
2. ไปที่ [facebook.com](https://facebook.com) และ login
3. คลิก Cookie-Editor icon → Export → JSON
4. save เป็น `fb_cookies.json`
5. รัน:

```bash
fb-reel-dl "https://www.facebook.com/your-profile/reels_tab" --cookies fb_cookies.json
```

---

## 🚨 แก้ไขปัญหา

| ปัญหา | สาเหตุ | วิธีแก้ |
|-------|--------|--------|
| `SessionNotCreatedException` | Chrome/Chromium ไม่ได้ติดตั้ง | `playwright install chromium` |
| ไม่พบ reel | ยังไม่ได้ login | ใช้ `--visible` หรือ `--cookies` |
| Popup จัดการไม่ได้ | FB เปลี่ยน UI | ลอง `--visible` เพื่อจัดการเอง |
| yt-dlp error | ติดตั้งไม่ถูกต้อง | `pip install -U yt-dlp` |
| `ModuleNotFoundError` | ขาด dependency | `pip install -r requirements.txt` |

---

## 📦 Dependencies

| Package | Version | ใช้ทำอะไร |
|---------|---------|-----------|
| [playwright](https://playwright.dev/) | >= 1.40 | Browser automation (scroll, collect URLs) |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | >= 2024 | Video download engine |

---

## 📝 License

MIT © [nanofatdog](https://github.com/nanofatdog)

---

## 🙏 Credits

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — คอมมูนิตี้ downloader ที่ดีที่สุด
- [Playwright](https://playwright.dev/) — Microsoft's browser automation
- [duongxthanh/facebook-reels-downloader](https://github.com/duongxthanh/facebook-reels-downloader) — inspiration
