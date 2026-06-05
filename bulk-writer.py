#!/usr/bin/env python3
"""Bulk Content Writer for Truffle News — dùng Ollama Qwen2.5:7b viết 20 bài SEO"""
import subprocess, sys, os, re, time
from datetime import datetime, timezone, timedelta

VIETNAM_TZ = timezone(timedelta(hours=7))
NOW = datetime.now(VIETNAM_TZ)
BLOG = "/mnt/g/truffle-news"
HUGO = "/home/tai_nguyen/.local/bin/hugo"
os.chdir(BLOG)

TOPICS = [
    "SEO Là Gì? Hướng Dẫn SEO Cơ Bản Cho Người Mới Bắt Đầu 2026",
    "Google Search Console: Hướng Dẫn Cài Đặt Và Sử Dụng Chi Tiết",
    "Google Analytics 4: Cách Theo Dõi Traffic Website Hiệu Quả",
    "Tốc Độ Tải Trang Ảnh Hưởng SEO Thế Nào? 7 Cách Cải Thiện",
    "Nghiên Cứu Từ Khoá: Cách Tìm Keyword Lên Top Google",
    "On-Page SEO: Checklist 20 Yếu Tố Tối Ưu Trang Web",
    "Off-Page SEO Là Gì? Khác Biệt Với On-Page SEO",
    "Google AI Overviews: Cách Tối Ưu Nội Dung Cho AI Search",
    "Core Web Vitals Là Gì? 3 Chỉ Số Google Dùng Đánh Giá Website",
    "Mobile SEO: Tối Ưu Website Cho Điện Thoại Di Động 2026",
    "Local SEO: Cách Đưa Doanh Nghiệp Lên Google Maps",
    "Technical SEO: Audit Kỹ Thuật Website Từ A Đến Z",
    "Content SEO: Cách Viết Bài Chuẩn SEO Không Bị Google Phạt",
    "Keyword Mapping: Xây Dựng Chiến Lược Từ Khoá Cho Website",
    "Link Building: Chiến Thuật Xây Backlink An Toàn 2026",
    "SEO Images: Cách Tối Ưu Hình Ảnh Cho Google Tìm Kiếm",
    "Internal Link: Chiến Thuật Liên Kết Nội Bộ Tăng SEO",
    "SEO Audit: Hướng Dẫn Kiểm Tra Website Toàn Diện",
    "SEO YouTube: Tối Ưu Video Lên Top Tìm Kiếm",
    "SEO Thương Mại Điện Tử: Tối Ưu Website Bán Hàng",
]

def log(msg):
    print(f"[{datetime.now(VIETNAM_TZ).strftime('%H:%M')}] {msg}")

def slugify(text):
    s = text.lower()
    for src, dst in [('á','a'),('à','a'),('ả','a'),('ã','a'),('ạ','a'),
                     ('ă','a'),('ắ','a'),('ằ','a'),('ẳ','a'),('ẵ','a'),('ặ','a'),
                     ('â','a'),('ấ','a'),('ầ','a'),('ẩ','a'),('ẫ','a'),('ậ','a'),
                     ('é','e'),('è','e'),('ẻ','e'),('ẽ','e'),('ẹ','e'),
                     ('ê','e'),('ế','e'),('ề','e'),('ể','e'),('ễ','e'),('ệ','e'),
                     ('í','i'),('ì','i'),('ỉ','i'),('ĩ','i'),('ị','i'),
                     ('ó','o'),('ò','o'),('ỏ','o'),('õ','o'),('ọ','o'),
                     ('ô','o'),('ố','o'),('ồ','o'),('ổ','o'),('ỗ','o'),('ộ','o'),
                     ('ơ','o'),('ớ','o'),('ờ','o'),('ở','o'),('ỡ','o'),('ợ','o'),
                     ('ú','u'),('ù','u'),('ủ','u'),('ũ','u'),('ụ','u'),
                     ('ư','u'),('ứ','u'),('ừ','u'),('ử','u'),('ữ','u'),('ự','u'),
                     ('ý','y'),('ỳ','y'),('ỷ','y'),('ỹ','y'),('ỵ','y'),
                     ('đ','d'),
                     ('?',''),(',',''),('!',''),(':',''),('"',''),("'",""),
                     ('  ',' ')]:
        s = s.replace(src, dst)
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'\s+', '-', s.strip())
    s = re.sub(r'-+', '-', s)
    return s[:80]

def build_prompt(title):
    return f"""Viết một bài blog SEO bằng tiếng Việt với chủ đề: {title}.

Yêu cầu:
- Viết bằng tiếng Việt tự nhiên, giọng chuyên nghiệp, dễ đọc
- Độ dài: 500-800 từ
- Có heading H2, H3 rõ ràng
- Có phần mở đầu hấp dẫn, kết luận
- Có mẹo thực tế (dạng bullet points)
- KHÔNG viết chung chung — nội dung cụ thể, có ví dụ
- KHÔNG thêm markdown frontmatter (---)
- KHÔNG thêm title/date/tags
- Chỉ viết phần content, bắt đầu bằng H1 (# Tiêu đề)"""

def call_ollama(prompt):
    """Gọi Ollama, trả về text hoặc None nếu fail"""
    try:
        r = subprocess.run(
            ["ollama", "run", "qwen2.5:7b-128k", prompt],
            capture_output=True, text=True, timeout=300
        )
        if r.returncode != 0:
            return None
        text = r.stdout
        # Clean ANSI
        text = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', text)
        text = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', text)
        text = re.sub(r'\x1b\[?[0-9;]*[a-zA-Z]', '', text)
        text = re.sub(r'[^\x20-\x7E\x0A\x0D\u00C0-\u1EF9]', '', text)
        return text.strip()
    except Exception as e:
        log(f"⚠️ Ollama error: {e}")
        return None

def write_post(title, body):
    slug = slugify(title)
    tags = "  - SEO\n  - " + title.split(":")[0].strip() if ":" in title else "  - SEO"
    
    # Chỉ lấy keyword đầu tiên (trước dấu ? hoặc :)
    kw = title.split("?")[0].split(":")[0].strip()
    tags = f"  - SEO\n  - {kw}"
    
    frontmatter = f"""---
title: "{title}"
date: {NOW.strftime('%Y-%m-%dT%H:%M:%S%z')}
tags:
{tags}
categories:
  - SEO
draft: false
---

"""
    footer = """

---

*Bài viết được tạo bởi **Content Lead AI** — Ascend SEO Company, thành viên của PigWorks Group 🐗*"""

    path = f"content/posts/{slug}.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(frontmatter + body + footer)
    return path

# === MAIN ===
print("🍄 Truffle News — Bulk Content Writer")
print("=" * 40)
print(f"Total: {len(TOPICS)} articles | Model: Qwen2.5:7b (Ollama)")
print()

success = 0
for i, topic in enumerate(TOPICS, 1):
    print(f"\n📝 [{i}/{len(TOPICS)}] {topic}")
    print("-" * 50)
    
    prompt = build_prompt(topic)
    body = call_ollama(prompt)
    
    if not body:
        log(f"❌ Failed, skipping...")
        continue
    
    path = write_post(topic, body)
    log(f"✅ Written: {path}")
    success += 1
    
    # Pause giữa các bài để không quá tải Ollama
    if i < len(TOPICS):
        time.sleep(2)

print(f"\n{'='*40}")
print(f"🎉 Complete! {success}/{len(TOPICS)} articles written.")

if success == 0:
    print("❌ Nothing to build. Exiting.")
    sys.exit(1)

# Build Hugo
print("\n🏗️ Building Hugo...")
r = subprocess.run(
    [HUGO, "--gc", "--minify", "-d", "docs"],
    capture_output=True, text=True, timeout=120
)
if r.returncode != 0:
    print(f"❌ Hugo build failed: {r.stderr[:300]}")
    sys.exit(1)
print("✅ Hugo build OK")

# Push
print("\n📤 Pushing to GitHub...")
r = subprocess.run(
    "git add -A && git commit -m 'bulk: {success} bài SEO Content Lead AI' && git push origin main 2>&1",
    shell=True, capture_output=True, text=True, timeout=120
)
print(r.stdout[-500:] if r.stdout else r.stderr[:500])
print("\n🎯 All done! https://tainguyen1804.github.io/truffle-news/")
