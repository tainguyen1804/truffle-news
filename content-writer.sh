#!/bin/bash
# Content Lead — viết bài SEO cho Truffle News dùng Ollama Qwen2.5:7b
# Usage: ./content-writer.sh "<title>" "<keyword1,keyword2>" "<category>"
# Output: content/posts/<slug>.md (Hugo ready)

set -euo pipefail

TITLE="${1:-}"
KEYWORDS="${2:-}"
CATEGORY="${3:-Công nghệ}"
DATE=$(date '+%Y-%m-%dT%H:%M:%S%z')
BLOG_DIR="/mnt/g/truffle-news"

if [ -z "$TITLE" ]; then
  echo "❌ Usage: $0 '<title>' '<keyword1,keyword2>' '<category>'"
  echo "   Ví dụ: $0 'AI SEO là gì' 'AI SEO,SEO 2026,công cụ AI' 'Công nghệ'"
  exit 1
fi

# Generate slug
SLUG=$(echo "$TITLE" | iconv -f utf-8 -t ascii//TRANSLIT 2>/dev/null || echo "$TITLE" | sed 's/[^a-zA-Z0-9]/ /g')
SLUG=$(echo "$SLUG" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | sed 's/--*/-/g' | sed 's/^-//;s/-$//')

# Tách keywords thành tags
TAGS=$(echo "$KEYWORDS" | tr ',' '\n' | sed 's/^ *//;s/ *$//' | sed 's/^/  - /')

# Prompt cho Ollama
PROMPT="Viết một bài blog SEO bằng tiếng Việt với chủ đề: $TITLE.
Từ khoá chính: $KEYWORDS.
Độ dài: 800-1200 từ.
Yêu cầu:
- Viết bằng tiếng Việt tự nhiên, giọng chuyên nghiệp
- Có heading H2, H3 rõ ràng
- Dùng từ khoá tự nhiên trong bài
- Có phần mở đầu hấp dẫn, kết luận
- Thêm mẹo/thủ thuật thực tế (dạng bullet points)
- Không viết chung chung, cần nội dung cụ thể
- PHẦN QUAN TRỌNG: CHỈ viết phần content thôi. KHÔNG thêm markdown frontmatter (---), KHÔNG thêm title/date/tags.
- Viết dưới dạng markdown đầy đủ
- Bắt đầu bằng 1-2 câu mở đầu mạnh mẽ, kết thúc bằng Kết Luận

Bài này đăng lên blog công nghệ, đối tượng là dân IT Việt Nam."

echo "🌀 Ollama is thinking..."
BODY=$(ollama run qwen2.5:7b-128k "$PROMPT" 2>/dev/null)

# Check if Ollama returned something
if [ -z "$BODY" ]; then
  echo "❌ Ollama returned empty. Using fallback..."
  BODY="Bài viết đang được cập nhật. Vui lòng quay lại sau."
fi

# Escape for sed - replace | with \n in body for embedding
BODY_ESCAPED=$(echo "$BODY" | python3 -c "import sys; print(sys.stdin.read())" 2>/dev/null)

# Write Hugo post
mkdir -p "$BLOG_DIR/content/posts"
cat > "$BLOG_DIR/content/posts/$SLUG.md" << POSTEOF
---
title: "$TITLE"
date: $DATE
tags:
$TAGS
categories:
  - $CATEGORY
draft: false
---

$BODY

---

*Bài viết được tạo bởi **Content Lead AI** — Ascend SEO Company, thành viên của PigWorks Group 🐗*
POSTEOF

echo "✅ Done: content/posts/$SLUG.md"
echo ""
echo "📝 Xem trước: head -80 $BLOG_DIR/content/posts/$SLUG.md"
