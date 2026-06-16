#!/bin/bash
# post-compact.sh — Compact 后自动恢复关键上下文
set -euo pipefail

source "$(dirname "$0")/lib/common.sh"

ROOT=$(project_root)
BOOK_DIR=$(discover_active_book)

echo "=== Post-Compact: Restoring writing context ==="

if [ -n "$BOOK_DIR" ] && [ -f "$BOOK_DIR/追踪/上下文.md" ]; then
  LINE_COUNT=$(wc -l < "$BOOK_DIR/追踪/上下文.md" | tr -d ' ')
  echo ""
  echo "📖 上下文文件: ${BOOK_DIR#$ROOT/}/追踪/上下文.md ($LINE_COUNT lines)"
  echo ""

  # 提取概览层信息（若存在）
  if grep -q "当前卷" "$BOOK_DIR/追踪/上下文.md" 2>/dev/null; then
    echo "--- 当前进度 ---"
    grep -A 10 "^## 概览层" "$BOOK_DIR/追踪/上下文.md" | head -10
    echo ""
  fi

  # 提取最近的章节信息
  if grep -q "### 第" "$BOOK_DIR/追踪/上下文.md" 2>/dev/null; then
    echo "--- 最近章节 ---"
    grep -A 2 "^### 第" "$BOOK_DIR/追踪/上下文.md" | head -12
    echo ""
  fi

  # 检查 run-ledger 中的最近操作
  if [ -f "$BOOK_DIR/追踪/run-ledger.md" ]; then
    echo "--- 最近操作 ---"
    tail -3 "$BOOK_DIR/追踪/run-ledger.md"
    echo ""
  fi

  echo "💡 提示: 请读取 ${BOOK_DIR#$ROOT/}/追踪/上下文.md 恢复完整写作状态。"
  echo "   关键命令: Read $BOOK_DIR/追踪/上下文.md"
else
  echo "⚠️  未找到活跃写作项目或上下文文件。"
  echo "   请手动检查项目状态。"
fi

echo "=== Post-Compact Complete ==="
