#!/bin/bash
# post-compact.sh — Compact 后自动恢复关键上下文
# v2: 增强 resume 显示 — 读取 contract + outline + 前一章路径，向用户展示 resume 点
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

  # === v2: Enhanced resume point detection ===

  # Detect current chapter
  CURRENT_CHAPTER=$(grep -oE '第[0-9]+章' "$BOOK_DIR/追踪/上下文.md" | tail -1 | grep -oE '[0-9]+' || echo "")
  if [ -z "$CURRENT_CHAPTER" ]; then
    # Try detecting from 正文/
    CURRENT_CHAPTER=$(ls -1 "$BOOK_DIR/正文/" 2>/dev/null | grep -oE '第[0-9]+章' | grep -oE '[0-9]+' | sort -n | tail -1 || echo "")
  fi

  if [ -n "$CURRENT_CHAPTER" ]; then
    CHAPTER_NUM=$(printf "%03d" "$CURRENT_CHAPTER")
    NEXT_CHAPTER=$(printf "%03d" $((10#$CURRENT_CHAPTER + 1)))

    echo "--- Resume 诊断 ---"
    echo "当前进度: 第${CURRENT_CHAPTER}章"
    echo "下一章: 第${NEXT_CHAPTER}章"
    echo ""

    # Check contract file for next chapter
    CONTRACT_FILE="$BOOK_DIR/.story-system/contracts/chapter_${NEXT_CHAPTER}.contract.md"
    if [ -f "$CONTRACT_FILE" ]; then
      echo "✅ 合约文件就绪: .story-system/contracts/chapter_${NEXT_CHAPTER}.contract.md"
    else
      echo "⚠️  合约文件缺失: .story-system/contracts/chapter_${NEXT_CHAPTER}.contract.md — 请先生成合约"
    fi

    # Check outline file for next chapter
    OUTLINE_FILE="$BOOK_DIR/大纲/细纲_第${NEXT_CHAPTER}章.md"
    if [ -f "$OUTLINE_FILE" ]; then
      echo "✅ 细纲文件就绪: 大纲/细纲_第${NEXT_CHAPTER}章.md"
    else
      echo "⚠️  细纲文件缺失: 大纲/细纲_第${NEXT_CHAPTER}章.md — 请先补建细纲"
    fi

    # Check previous chapter body
    PREV_BODY=$(ls -1 "$BOOK_DIR/正文/" 2>/dev/null | grep "第0*${CURRENT_CHAPTER}章" | head -1 || echo "")
    if [ -n "$PREV_BODY" ]; then
      echo "✅ 上一章正文: 正文/${PREV_BODY}"
    else
      echo "⚠️  上一章正文未找到"
    fi

    # Show run-ledger resume point
    if [ -f "$BOOK_DIR/追踪/run-ledger.md" ]; then
      echo ""
      echo "--- 最近操作 (run-ledger) ---"
      # Exclude context_compact events from default display
      tail -20 "$BOOK_DIR/追踪/run-ledger.md" | grep -v "context_compact" | tail -5
      echo ""

      # Check for interrupted operation
      LAST_STATUS=$(tail -1 "$BOOK_DIR/追踪/run-ledger.md" | grep -oE '\| *[a-z_]+ *\|' | tr -d '| ' || echo "")
      if [ "$LAST_STATUS" = "interrupted" ] || [ "$LAST_STATUS" = "failed" ]; then
        LAST_STEP=$(tail -1 "$BOOK_DIR/追踪/run-ledger.md" | awk -F'|' '{print $2}' | tr -d ' ' || echo "unknown")
        echo "🔴 检测到中断: 最后步骤 '${LAST_STEP}' 状态为 ${LAST_STATUS}"
        echo "   💡 使用 --resume 从断点继续"
      fi
    fi
  fi

  echo ""
  echo "💡 提示: 请读取以下文件恢复完整写作状态:"
  echo "   1. 上下文: Read $BOOK_DIR/追踪/上下文.md"
  echo "   2. 合约文件: Read $BOOK_DIR/.story-system/contracts/chapter_${NEXT_CHAPTER}.contract.md"
  echo "   3. 上一章正文: Read $BOOK_DIR/正文/第${CURRENT_CHAPTER}章_*.md"
  echo "   4. 细纲: Read $BOOK_DIR/大纲/细纲_第${NEXT_CHAPTER}章.md"
else
  echo "⚠️  未找到活跃写作项目或上下文文件。"
  echo "   请手动检查项目状态。"
fi

echo "=== Post-Compact Complete ==="
