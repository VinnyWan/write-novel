#!/bin/bash
# pre-compact.sh — compact 前强制保存写作状态到追踪/上下文.md
set -euo pipefail

source "$(dirname "$0")/lib/common.sh"

ROOT=$(project_root)
BOOK_DIR=$(discover_active_book)

echo "=== Pre-Compact: Saving writing state ==="

if [ -n "$BOOK_DIR" ]; then
  CONTEXT_FILE="$BOOK_DIR/追踪/上下文.md"

  # 确保追踪目录存在
  mkdir -p "$BOOK_DIR/追踪"

  # 如果上下文文件不存在，创建模板
  if [ ! -f "$CONTEXT_FILE" ]; then
    cat > "$CONTEXT_FILE" << 'TEMPLATE'
# 上下文

## 精简层（最近 5 章详情）

<!-- 每章完成后由 agent 自动更新 -->

## 摘要层（10 章概要）

<!-- 自动从精简层降级 -->

## 概览层

<!-- 卷级概览，由 agent 每次完成章节后更新 -->

> 此文件由 pre-compact hook 自动维护。Compact 后请读取此文件恢复上下文。
TEMPLATE
  fi

  # 记录 compact 时间戳
  echo "## Compact 记录" >> "$CONTEXT_FILE"
  echo "- Compact 时间: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$CONTEXT_FILE"
  echo "- Git 状态: $(git -C "$ROOT" diff --name-only 2>/dev/null | wc -l | tr -d ' ') unstaged files" >> "$CONTEXT_FILE"

  LINE_COUNT=$(wc -l < "$CONTEXT_FILE" | tr -d ' ')
  echo "Writing state saved: ${BOOK_DIR#$ROOT/}/追踪/上下文.md ($LINE_COUNT lines)"
else
  echo "No active book found. State not saved."
fi

# Git 状态摘要
CHANGED=$(git -C "$ROOT" diff --name-only 2>/dev/null | wc -l | tr -d ' ') || CHANGED=0
STAGED=$(git -C "$ROOT" diff --name-only --cached 2>/dev/null | wc -l | tr -d ' ') || STAGED=0
echo "Git: ${CHANGED} unstaged, ${STAGED} staged"

echo "=== Pre-Compact Complete ==="
