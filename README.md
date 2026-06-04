# fb_reel_dl 📱

> **Facebook Reels Bulk Downloader** — ดาวน์โหลด Reels ทั้งหมดจาก Facebook Profile
> ด้วย Playwright + yt-dlp แบบ自动化 (Automated scroll + download)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎯 **Bulk download** | Scroll infinite scroll เก็บ reel URLs ทั้งหมด → ดาวน์โหลด |
| 🕵️ **Headless mode** | รันแบบไม่เห็น browser (default) |
| 👁️ **Visible mode** | เห็น browser UI — ใช้ login ด้วยตนเองได้ |
| 🍪 **Cookie support** | รองรับ cookies JSON — ไม่ต้อง login ทุกครั้ง |
| 📋 **Dry-run mode** | แค่เก็บ URL list, ยังไม่โหลดวิดีโอ |
| 📊 **CSV export** | บันทึก reel_id + URL เป็น CSV |
| 🧹 **Auto-cleanup** | ตัด tracking params, deduplicate reel URLs |
| 🚀 **yt-dlp backend** | ความเร็วสูง, รองรับ resume, retry |

---

## 🔧 Installation

### วิธีที่ 1: One-liner (curl → bash) 🚀

```bash
curl -sL https://raw.githubusercontent.com/nanofatdog/fb_reel_dl/main/install.sh | bash
```

### วิธีที่ 2: Manual

```bash
# Clone
git clone https://github.com/nanofatdog/fb_reel_dl.git
cd fb_reel_dl

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser (Chromium)
playwright install chromium

# พร้อมใช้งาน!
python fb_reel_dl.py --help
```

### วิธีที่ 3: pip install (อนาคต)

```bash
# (coming soon)
pip install fb-reel-dl
```

---

## 📖 วิธีใช้

### 🎬 ดาวน์โหลด reels ทั้งหมด (headless)

```bash
python fb_reel_dl.py "https://www.facebook.com/profile.php?id=100080117672198&sk=reels_tab"
```

### 👁️ เห็น browser UI (login ด้วยตนเอง)

```bash
python fb_reel_dl.py "https://www.facebook.com/..." --visible
```

พอ browser เปิดขึ้นมา:
1. Login Facebook (ถ้ายังไม่ login)
2. สคริปต์จะ scroll เก็บ reels ให้อัตโนมัติ
3. กด Ctrl+C เพื่อหยุดได้ทุกเมื่อ

### 🍪 ใช้ cookies (ไม่ต้อง login ทุกครั้ง)

Export cookies จาก browser extension เช่น [Cookie-Editor](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)
→ Export → JSON → แล้วใช้:

```bash
python fb_reel_dl.py <url> --cookies fb_cookies.json
```

### 📋 แค่เก็บ URLs (ไม่โหลด)

```bash
python fb_reel_dl.py <url> --dry-run
```

ได้ไฟล์:
- `downloads/<channel>/reels_list.csv` — reel_id + URL
- `downloads/<channel>_urls.txt` — plain URLs

### 🏷️ กำหนดชื่อ output folder

```bash
python fb_reel_dl.py <url> --name my_channel
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
    └── <channel_name>/     # เปลี่ยนได้ด้วย --name
        ├── reel_12345.mp4
        ├── reel_67890.mp4
        └── ...
    └── <channel_name>_urls.txt   # URL list
```

---

## ⚙️ How it works — วิธีการทำงาน

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
python fb_reel_dl.py "https://www.facebook.com/profile.php?id=..." --cookies fb_cookies.json
```

---

## 🚨 Troubleshooting

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
