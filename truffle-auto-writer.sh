#!/bin/bash
# Truffle News Auto Writer Script
# Chạy mỗi 5h: tìm tin AI hot → viết bài Hugo → build → push

set -e
cd /mnt/g/truffle-news

# Log
echo "[$(date '+%Y-%m-%d %H:%M')] 🍄 Truffle News Auto Writer starting..."

# Lấy tin hot từ web
echo "[$(date '+%Y-%m-%d %H:%M')] Searching for trending news..."
TRENDING=$(curl -s "https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=5" 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for hit in data.get('hits', [])[:5]:
        title = hit.get('title', '')
        url = hit.get('url') or f'https://news.ycombinator.com/item?id={hit.get(\"objectID\")}'
        print(f'- [{title}]({url})')
except: pass
" 2>/dev/null)

if [ -z "$TRENDING" ]; then
    echo "[$(date)] ⚠️ No trending data from Hacker News, skipping..."
    exit 0
fi

# Tạo bài viết mới
DATE=$(date +%Y-%m-%d)
SLUG="tin-cong-nghe-$(date +%d-%m-%Y)"
TITLE="Tin Công Nghệ Nóng Trong Ngày — $(date '+%d/%m/%Y')"

cat > "content/posts/$SLUG.md" << EOF
---
title: "$TITLE"
date: $(date +%Y-%m-%dT%H:%M:%S%z)
tags:
  - Tin Nóng
  - AI
  - Công Nghệ
categories:
  - Công nghệ
---

Dưới đây là những tin tức công nghệ đang được quan tâm nhất trong ngày hôm nay, tổng hợp từ nhiều nguồn uy tín.

<!--more-->

$TRENDING

---

*Bài viết được tổng hợp tự động bởi Truffle News 🍄*
EOF

echo "[$(date)] ✅ Article written: content/posts/$SLUG.md"

# Build Hugo
echo "[$(date)] Building site..."
~/.local/bin/hugo --gc --minify -d docs 2>&1

# Push lên git
echo "[$(date)] Pushing to GitHub..."
git add -A
git commit -m "auto: $TITLE"
git push origin main 2>&1

echo "[$(date)] ✅ Done! Article published: $TITLE"
