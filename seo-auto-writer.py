#!/usr/bin/env python3
"""Truffle News SEO Auto Writer — dùng Ollama viết 1 bài SEO mới mỗi lần chạy"""
import subprocess, sys, os, re, json
from datetime import datetime, timezone, timedelta

VIETNAM_TZ = timezone(timedelta(hours=7))
NOW = datetime.now(VIETNAM_TZ)
BLOG = "/mnt/g/truffle-news"
HUGO = "/home/tai_nguyen/.local/bin/hugo"

# Queue các chủ đề SEO — mỗi lần chạy lấy 1 topic từ file queue
QUEUE_FILE = os.path.join(BLOG, ".seo-queue.json")
DONE_FILE = os.path.join(BLOG, ".seo-done.json")

# Khởi tạo queue nếu chưa có
DEFAULT_TOPICS = [
    "SEO Website Bất Động Sản: Chiến Lược Tối Ưu Toàn Diện",
    "SEO Y Tế: Tối Ưu Website Bệnh Viện Phòng Khám",
    "SEO Giáo Dục: Đưa Trung Tâm Lên Top Google",
    "SEO Du Lịch: Cách Tối Ưu Website Tour Du Lịch",
    "SEO Ẩm Thực: Tối Ưu Website Nhà Hàng Quán Ăn",
    "SEO Thời Trang: Chiến Lược Content Cho Shop Quần Áo",
    "SEO Game: Tối Ưu Website Game Online",
    "SEO Tin Tức: Cách Viết Tin Tức Chuẩn SEO",
    "SEO Landing Page: Tối Ưu Trang Đích Chuyển Đổi Cao",
    "SEO SaaS: Chiến Lược SEO Cho Phần Mềm Đám Mây",
    "SEO Công Ty Luật: Đưa Dịch Vụ Pháp Lý Lên Top",
    "SEO Tài Chính: Tối Ưu Website Ngân Hàng Bảo Hiểm",
    "SEO Xuất Nhập Khẩu: Tối Ưu Website Logistics",
    "SEO Mỹ Phẩm: Chiến Lược Content Cho Beauty Brand",
    "SEO Thể Thao: Tối Ưu Website Tin Thể Thao",
    "SEO Việc Làm: Đưa Website Tuyển Dụng Lên Top",
    "SEO Công Nghệ Thông Tin: Tối Ưu Website IT",
    "SEO Nội Thất: Chiến Lược Từ Khoá Cho Shop Nội Thất",
    "SEO Ô Tô: Tối Ưu Website Showroom Xe Hơi",
    "SEO Ngân Hàng: Tối Ưu Từ Khoá Tài Chính"
]

def load_json(path, default):
    try:
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
    except: pass
    return default

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, ensure_ascii=False)

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
                     ('đ','d')]:
        s = s.replace(src, dst)
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'\s+', '-', s.strip())
    return re.sub(r'-+', '-', s)[:80]

PROMPT_TEMPLATE = """Viết một bài blog SEO bằng tiếng Việt với chủ đề: {title}.

Yêu cầu:
- Viết bằng tiếng Việt tự nhiên, giọng chuyên nghiệp, dễ đọc
- Độ dài: 500-800 từ
- Có heading H2, H3 rõ ràng
- Có phần mở đầu hấp dẫn, kết luận
- Có mẹo thực tế (dạng bullet points)
- KHÔNG viết chung chung — nội dung cụ thể, có ví dụ
- KHÔNG thêm frontmatter
- Chỉ viết phần content, bắt đầu bằng H1"""

def write_post(title, body):
    slug = slugify(title)
    kw = title.split(":")[0].strip()
    frontmatter = f"""---
title: "{title}"
date: {NOW.strftime('%Y-%m-%dT%H:%M:%S%z')}
tags:
  - SEO
  - {kw}
categories:
  - SEO
draft: false
---

"""
    footer = "\n\n---\n\n*Bài viết được tạo bởi **Content Lead AI** — Ascend SEO Company, PigWorks Group 🐗*"
    
    path = f"content/posts/{slug}.md"
    os.chdir(BLOG)
    with open(path, "w", encoding="utf-8") as f:
        f.write(frontmatter + body + footer)
    return path

os.chdir(BLOG)

# Load queue
queue = load_json(QUEUE_FILE, DEFAULT_TOPICS)
done = load_json(DONE_FILE, [])

if not queue:
    # Hết queue → xào lại + thêm topic mới
    print("📋 Queue hết, tạo queue mới...")
    queue = DEFAULT_TOPICS.copy()
    done = []
    
topic = queue.pop(0)

print(f"🍄 Truffle News — SEO Auto Writer")
print(f"📝 Topic: {topic}")
print(f"📊 Queue còn lại: {len(queue)} topics")

# Gọi Ollama
prompt = PROMPT_TEMPLATE.format(title=topic)
try:
    r = subprocess.run(
        ["ollama", "run", "qwen2.5:7b-128k", prompt],
        capture_output=True, text=True, timeout=300
    )
    if r.returncode != 0:
        print(f"❌ Ollama failed: {r.stderr[:200]}")
        queue.insert(0, topic)  # put back
        save_json(QUEUE_FILE, queue)
        sys.exit(1)
    
    body = r.stdout
    # Clean ANSI
    body = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', body)
    body = body.strip()
    
    if not body or len(body) < 100:
        print("❌ Content quá ngắn, skip...")
        queue.insert(0, topic)
        save_json(QUEUE_FILE, queue)
        sys.exit(1)
    
    path = write_post(topic, body)
    done.append({"topic": topic, "path": path, "time": NOW.isoformat()})
    save_json(DONE_FILE, done)
    save_json(QUEUE_FILE, queue)
    print(f"✅ Written: {path}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    queue.insert(0, topic)
    save_json(QUEUE_FILE, queue)
    sys.exit(1)

# Build Hugo
print("🏗️ Building Hugo...")
r = subprocess.run([HUGO, "--gc", "--minify", "-d", "docs"],
                   capture_output=True, text=True, timeout=120)
if r.returncode != 0:
    print(f"❌ Hugo build failed: {r.stderr[:300]}")
    sys.exit(1)
print(f"✅ Hugo OK — {len(r.stdout.splitlines())} pages")

# Push
print("📤 Pushing to GitHub...")
r = subprocess.run(
    "git add -A && git commit -m 'auto: {topic}' && git push origin main 2>&1".format(topic=topic),
    shell=True, capture_output=True, text=True, timeout=120
)
print(f"✅ Push OK" if r.returncode == 0 else f"❌ Push failed: {r.stderr[:200]}")

print(f"\n🎯 Bài hôm nay: {topic}")
print(f"📚 Queue còn: {len(queue)} topics")
