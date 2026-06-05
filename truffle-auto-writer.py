#!/usr/bin/env python3
"""Truffle News Auto Writer — mỗi 5h: lấy tin AI hot → viết bài Hugo → build → push"""
import subprocess, json, sys, os, re
from datetime import datetime, timezone, timedelta

VIETNAM_TZ = timezone(timedelta(hours=7))
NOW = datetime.now(VIETNAM_TZ)
WORKDIR = "/mnt/g/truffle-news"
os.chdir(WORKDIR)

def log(msg):
    print(f"[{NOW.strftime('%Y-%m-%d %H:%M')}] {msg}")

def run(cmd, check=True):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)

# === STEP 1: Lấy tin hot từ HN + multi-source ===
log("🔍 Searching for trending news...")

# Hacker News front page
hits = []
try:
    r = run("curl -s 'https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=10'")
    data = json.loads(r.stdout)
    for hit in data.get("hits", []):
        title = hit.get("title", "").strip()
        url = hit.get("url") or ""
        if title and "show hn" not in title.lower() and "ask hn" not in title.lower():
            hits.append({"title": title, "url": url, "source": "Hacker News"})
except Exception as e:
    log(f"⚠️ HN fetch error: {e}")

# Lọc bài về AI/tech
tech_keywords = ["ai", "llm", "gpt", "model", "agent", "robot", "code", "github", "open", "nvidia", 
                 "apple", "google", "microsoft", "meta", "anthropic", "openai", "gemini", "claude",
                 "deep", "learning", "neural", "gpu", "chip", "startup", "funding", "valuation",
                 "quantum", "blockchain", "crypto", "security", "privacy", "data", "cloud"]

tech_hits = [h for h in hits if any(kw in h["title"].lower() for kw in tech_keywords)]
hits_to_use = tech_hits[:5] if len(tech_hits) >= 2 else hits[:5]

if not hits_to_use:
    log("⚠️ No news found, aborting")
    sys.exit(0)

log(f"📰 Found {len(hits_to_use)} stories to write")

# === STEP 2: Viết bài ===
today = NOW.strftime("%d/%m/%Y")
slug = f"tin-cong-nghe-{NOW.strftime('%d-%m-%Y')}"
tags = ["Tin Nóng", "Công Nghệ"]
categories = ["Công nghệ"]

# Xác định nội dung dựa trên hits
articles_lines = []
for i, h in enumerate(hits_to_use, 1):
    title = h["title"]
    url = h["url"]
    source = h["source"]
    lines = [f"{'='*60}", f"**Bài {i}:** [{title}]({url})", f"*Nguồn: {source}*"]
    articles_lines.append("\n\n".join(lines))

articles_body = "\n\n---\n\n".join(articles_lines)

# Intro động
intro = f"Dưới đây là những tin tức công nghệ nóng nhất trong ngày hôm nay, được tổng hợp từ các nguồn uy tín quốc tế."

post = f"""---
title: "Tin Công Nghệ Nóng Trong Ngày — {today}"
date: {NOW.strftime('%Y-%m-%dT%H:%M:%S%z')}
tags:
  - Tin Nóng
  - Công Nghệ
categories:
  - Công Nghệ
---

{intro}

<!--more-->

{articles_body}

---

*Bài viết được tổng hợp tự động bởi **Truffle News** 🍄 — mang đến cho bạn những thông tin nhanh nhất, chính xác nhất.*
"""

post_path = f"content/posts/{slug}.md"
with open(post_path, "w", encoding="utf-8") as f:
    f.write(post)
log(f"✅ Written: {post_path}")

# === STEP 3: Build Hugo ===
log("🏗️ Building Hugo...")
r = run("~/.local/bin/hugo --gc --minify -d docs 2>&1")
if r.returncode != 0:
    log(f"❌ Hugo build failed: {r.stdout[:500]}")
    sys.exit(1)
log("✅ Hugo build OK")

# === STEP 4: Push ===
log("📤 Pushing to GitHub...")
r = run("git add -A && git commit -m 'auto: tin cong nghe {today}' && git push origin main 2>&1")
if r.returncode != 0:
    log(f"⚠️ Git push issue (possibly nothing to commit): {r.stdout[:300]}")
else:
    log(f"✅ Push OK")

log("🎉 Done!")
