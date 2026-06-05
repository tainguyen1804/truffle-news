#!/bin/bash
# Bulk Content Writer — viết 20 bài SEO cho Truffle News
# Dùng Ollama Qwen2.5:7b local (0 token)

set -euo pipefail

BLOG="/mnt/g/truffle-news"
WRITER="$BLOG/content-writer.sh"

TOPICS=(
  "SEO Là Gì? Hướng Dẫn SEO Cơ Bản Cho Người Mới Bắt Đầu 2026"
  "Google Search Console: Hướng Dẫn Cài Đặt Và Sử Dụng Chi Tiết"
  "Google Analytics 4: Cách Theo Dõi Traffic Website Hiệu Quả"
  "Tốc Độ Tải Trang Ảnh Hưởng SEO Thế Nào? 7 Cách Cải Thiện"
  "Nghiên Cứu Từ Khoá: Cách Tìm Keyword Lên Top Google"
  "On-Page SEO: Checklist 20 Yếu Tố Tối Ưu Trang Web"
  "Off-Page SEO Là Gì? Khác Biệt Với On-Page SEO"
  "Google AI Overviews: Cách Tối Ưu Nội Dung Cho AI Search"
  "Core Web Vitals Là Gì? 3 Chỉ Số Google Dùng Đánh Giá Website"
  "Mobile SEO: Tối Ưu Website Cho Điện Thoại Di Động 2026"
  "Local SEO: Cách Đưa Doanh Nghiệp Lên Google Maps"
  "Technical SEO: Audit Kỹ Thuật Website Từ A Đến Z"
  "Content SEO: Cách Viết Bài Chuẩn SEO Không Bị Google Phạt"
  "Keyword Mapping: Xây Dựng Chiến Lược Từ Khoá Cho Website"
  "Link Building: Chiến Thuật Xây Backlink An Toàn 2026"
  "SEO Images: Cách Tối Ưu Hình Ảnh Cho Google Tìm Kiếm"
  "Internal Link: Chiến Thuật Liên Kết Nội Bộ Tăng SEO"
  "SEO Audit: Hướng Dẫn Kiểm Tra Website Toàn Diện"
  "SEO YouTube: Tối Ưu Video Lên Top Tìm Kiếm"
  "SEO Thương Mại Điện Tử: Tối Ưu Website Bán Hàng"
)

echo "🍄 Truffle News — Bulk Content Writer"
echo "===================================="
echo "Total: ${#TOPICS[@]} articles"
echo "Model: Qwen2.5:7b (Ollama local)"
echo ""

mkdir -p "$BLOG/content/posts"

COUNT=0
for ((i=0; i<${#TOPICS[@]}; i++)); do
  TOPIC="${TOPICS[$i]}"
  COUNT=$((COUNT + 1))
  echo ""
  echo "📝 [$COUNT/${#TOPICS[@]}] $TOPIC"
  echo "──────────────────────────────────────────"
  
  bash "$WRITER" "$TOPIC" "$TOPIC" "SEO"
  
  echo "✅ [$COUNT] Done"
  echo ""
done

echo ""
echo "🎉 Complete! $COUNT articles written."
echo ""

# Build Hugo
echo "🏗️ Building Hugo..."
cd "$BLOG" && ~/.local/bin/hugo --gc --minify -d docs 2>&1
echo ""

# Push
echo "📤 Pushing to GitHub..."
git add -A
git commit -m "bulk: ${COUNT} bài SEO Content Lead AI"
git push origin main 2>&1
echo ""
echo "🎯 All done! https://tainguyen1804.github.io/truffle-news/"
