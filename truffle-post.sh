#!/bin/bash
# Truffle News — Post Writer & Publisher
# Usage: ./truffle-post.sh "Tiêu đề bài viết" thể-loại tag1,tag2 < content.md
# Output: Hugo markdown → build → commit → push

set -euo pipefail

SITE_DIR="/mnt/g/truffle-news"
HUGO_BIN="$HOME/.local/bin/hugo"

TITLE="${1:-}"
CATEGORY="${2:-Tin tức}"
TAGS="${3:-}"

if [ -z "$TITLE" ]; then
  echo "Usage: cat content.md | truffle-post.sh \"Tiêu đề\" [thể-loại] [tag1,tag2]"
  echo "   hoặc: truffle-post.sh --publish-only (chỉ build + push)"
  exit 1
fi

# 1. Tạo slug từ tiêu đề
SLUG=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' \
  | sed 's/[àáạảãâầấậẩẫăằắặẳẵ]/a/g; s/[èéẹẻẽêềếệểễ]/e/g; s/[ìíịỉĩ]/i/g; s/[òóọỏõôồốộổỗơờớợởỡ]/o/g; s/[ùúụủũưừứựửữ]/u/g; s/[ỳýỵỷỹ]/y/g; s/đ/d/g' \
  | sed 's/[^a-z0-9]/-/g; s/--*/-/g; s/^-//; s/-$//')
FILE="$SITE_DIR/content/posts/$SLUG.md"

# 2. Ghi file
CONTENT=$(cat)
DATE=$(date '+%Y-%m-%dT%H:%M:%S+07:00')

cat > "$FILE" << EOF
---
title: "$TITLE"
date: $DATE
categories: ["$CATEGORY"]
tags: [$(echo "$TAGS" | sed 's/[^,]\+/"&"/g' | sed 's/,/, /g')]
draft: false
---

$CONTENT
EOF

echo "✅ Đã lưu: $FILE"

# 3. Build Hugo
cd "$SITE_DIR"
$HUGO_BIN 2>&1

# 4. Git commit + push
cd "$SITE_DIR"
git add -A
git commit -m "truffle: $TITLE" 2>/dev/null || echo "ℹ️ Không có thay đổi mới"
git push 2>&1 || echo "⚠️ Push thất bại — chưa setup remote?"

echo "✅ Đã push lên GitHub: $TITLE"
