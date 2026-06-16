#!/bin/bash
# session-start.sh — 显示项目状态、大纲缓冲、伏笔状态、上次操作
set -euo pipefail

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ ! -f "$HOOK_DIR/lib/common.sh" ] || [ ! -f "$HOOK_DIR/lib/sentinel.sh" ]; then
  printf '%b' "[WARN] story hook 函数库缺失。重新运行 /story-setup 恢复。\n"
  exit 0
fi

source "$HOOK_DIR/lib/common.sh"
source "$HOOK_DIR/lib/sentinel.sh"

ROOT=$(project_root)
OUTPUT=""
HAS_CONTENT=false

# 部署自检
if sentinel_exists "$ROOT/.story-deployed"; then
  MISSING_HOOKS=""
  for hook in session-start.sh session-end.sh detect-story-gaps.sh pre-compact.sh post-compact.sh validate-story-commit.sh lib/common.sh lib/sentinel.sh; do
    if [ ! -f "$ROOT/.claude/hooks/$hook" ]; then
      MISSING_HOOKS+="$hook "
    fi
  done
  if [ -n "$MISSING_HOOKS" ]; then
    OUTPUT+="[WARN] 缺少 hook：$MISSING_HOOKS 重新运行 /story-setup。\n\n"
    HAS_CONTENT=true
  fi
else
  OUTPUT+="[WARN] 写作环境未部署。运行 /story-setup 初始化。\n\n"
  HAS_CONTENT=true
fi

# Git 状态
BRANCH=$(git -C "$ROOT" branch --show-current 2>/dev/null || echo "")
if [ -n "$BRANCH" ]; then
  OUTPUT+="=== 写作进度 ===\n分支：$BRANCH\n"
  RECENT=$(git -C "$ROOT" log --oneline -3 2>/dev/null || true)
  if [ -n "$RECENT" ]; then
    OUTPUT+="$RECENT\n"
  fi
  OUTPUT+="\n"
  HAS_CONTENT=true
fi

# 大纲缓冲余量
BOOK_DIR=$(discover_active_book)
if [ -n "$BOOK_DIR" ] && [ -d "$BOOK_DIR/大纲" ]; then
  OUTLINE_COUNT=$(find "$BOOK_DIR/大纲" -name "细纲_第*.md" 2>/dev/null | wc -l | tr -d ' ')
  CHAPTER_COUNT=$(find "$BOOK_DIR/正文" -name "Chapter-*.md" -o -name "第*章*.md" 2>/dev/null | wc -l | tr -d ' ')
  BUFFER=$((OUTLINE_COUNT - CHAPTER_COUNT))
  if [ "$OUTLINE_COUNT" -gt 0 ]; then
    OUTPUT+="[INFO] 细纲: ${OUTLINE_COUNT}章 | 已写: ${CHAPTER_COUNT}章 | 缓冲: ${BUFFER}章\n"
    if [ "$BUFFER" -le 2 ] && [ "$BUFFER" -ge 0 ]; then
      OUTPUT+="[WARN] 大纲缓冲不足 (≤2章)\n"
    fi
    HAS_CONTENT=true
  fi
fi

# 待处理伏笔
if [ -n "$BOOK_DIR" ] && [ -f "$BOOK_DIR/追踪/foreshadowing.md" ]; then
  PENDING=$(grep -c "未回收\|pending\|open" "$BOOK_DIR/追踪/foreshadowing.md" 2>/dev/null || echo "0")
  OVERDUE=$(grep -c "overdue\|逾期" "$BOOK_DIR/追踪/foreshadowing.md" 2>/dev/null || echo "0")
  if [ "$PENDING" -gt 0 ] 2>/dev/null; then
    OUTPUT+="[INFO] 待回收伏笔: ${PENDING}个"
    if [ "$OVERDUE" -gt 0 ] 2>/dev/null; then
      OUTPUT+=" (逾期${OVERDUE}个)"
    fi
    OUTPUT+="\n"
    HAS_CONTENT=true
  fi
fi

# 上次操作
if [ -n "$BOOK_DIR" ] && [ -f "$BOOK_DIR/追踪/run-ledger.md" ]; then
  LAST_OP=$(tail -1 "$BOOK_DIR/追踪/run-ledger.md" 2>/dev/null || echo "")
  if [ -n "$LAST_OP" ]; then
    OUTPUT+="[INFO] 上次: ${LAST_OP}\n"
    HAS_CONTENT=true
  fi
fi

# 上下文摘要
if [ -n "$BOOK_DIR" ] && [ -f "$BOOK_DIR/追踪/上下文.md" ]; then
  OUTPUT+="--- 进度摘要 ---\n"
  SNAPSHOT=$(head -10 "$BOOK_DIR/追踪/上下文.md")
  OUTPUT+="${SNAPSHOT}\n---\n\n"
  HAS_CONTENT=true
fi

# 未完成拆文
if [ -d "$ROOT/拆文库" ]; then
  PROGRESS_COUNT=$(find "$ROOT/拆文库" -name "_progress.md" 2>/dev/null | wc -l | tr -d ' ')
  if [ "$PROGRESS_COUNT" -gt 0 ]; then
    OUTPUT+="[INFO] 拆文库/ 中有 ${PROGRESS_COUNT} 个未完成拆文。\n"
    HAS_CONTENT=true
  fi
fi

if [ "$HAS_CONTENT" = true ]; then
  printf '%b' "$OUTPUT"
fi
