#!/bin/bash
# guard-outline-before-prose.sh — 正文写入前强制检查对应合约（优先）或细纲是否存在
# 阻断式 hook：无对应合约且无细纲时拒绝正文首次写入
# 触发条件：Write/Edit 工具，目标为 正文/ 目录下的 .md 文件
# v2: 优先检查 .story-system/contracts/ 合约文件，回退到细纲检查
set -euo pipefail

source "$(dirname "$0")/lib/common.sh"

INPUT=$(cat)
# 探测真正可用的解释器：Windows 上 `python3` 会命中 Microsoft Store 占位程序（exit 49）
PYBIN=""
for c in python3 python py; do
  if "$c" -c "" >/dev/null 2>&1; then PYBIN="$c"; break; fi
done
FILE_PATH=""
if [ -n "$PYBIN" ]; then
  FILE_PATH=$(echo "$INPUT" | "$PYBIN" -c "
import sys, json
try:
    data = json.load(sys.stdin)
    ti = data.get('tool_input', data.get('toolInput', data.get('input', {})))
    if isinstance(ti, dict):
        fp = ti.get('file_path', ti.get('path', ti.get('filename', '')))
    else:
        fp = str(ti)
    print(fp)
except:
    print('')
" 2>/dev/null || echo "")
fi

# Only check 正文/ directory writes
if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# Normalize path — only block files under 正文/ directory
if ! echo "$FILE_PATH" | grep -qE '(^|/)正文/'; then
    exit 0
fi

# Extract chapter number from filename
CHAPTER_NUM=$(echo "$FILE_PATH" | grep -oE '第0*([0-9]+)章' | grep -oE '[0-9]+' || echo "")
if [ -z "$CHAPTER_NUM" ]; then
    # Can't parse chapter number — allow
    exit 0
fi

CHAPTER_NUM=$(printf "%03d" "$CHAPTER_NUM")

ROOT=$(project_root)
BOOK_DIR=$(discover_active_book)

if [ -z "$BOOK_DIR" ]; then
    exit 0
fi

# Priority 1: Check contract file (.story-system/contracts/chapter_XXX.contract.md)
CONTRACT_FILE="$BOOK_DIR/.story-system/contracts/chapter_${CHAPTER_NUM}.contract.md"
if [ -f "$CONTRACT_FILE" ]; then
    # Contract exists — verify it has required frontmatter fields
    if head -1 "$CONTRACT_FILE" 2>/dev/null | grep -q "^---$"; then
        CONTRACT_FM=$(sed -n '2,/^---$/p' "$CONTRACT_FILE" 2>/dev/null | head -40)
        if [ -n "$CONTRACT_FM" ]; then
            # Check CBN (required)
            if ! echo "$CONTRACT_FM" | grep -qE "^cbn:" 2>/dev/null; then
                echo "{\"hookSpecificOutput\":{\"permissionDecision\":\"deny\"},\"systemMessage\":\"[guard-outline-before-prose] 合约文件缺少 CBN 字段: .story-system/contracts/chapter_${CHAPTER_NUM}.contract.md。请先补全合约再写正文。\"}" >&2
                exit 2
            fi
            # Check CEN (required)
            if ! echo "$CONTRACT_FM" | grep -qE "^cen:" 2>/dev/null; then
                echo "{\"hookSpecificOutput\":{\"permissionDecision\":\"deny\"},\"systemMessage\":\"[guard-outline-before-prose] 合约文件缺少 CEN 字段: .story-system/contracts/chapter_${CHAPTER_NUM}.contract.md。请先补全合约再写正文。\"}" >&2
                exit 2
            fi
        fi
    fi
    # Contract exists and has required fields — allow
    exit 0
fi

# Priority 2: Fallback to outline file (legacy projects without .story-system/)
OUTLINE_FILE="$BOOK_DIR/大纲/细纲_第${CHAPTER_NUM}章.md"
if [ -f "$OUTLINE_FILE" ]; then
    exit 0
fi

# Block: neither contract nor outline exists
echo "{\"hookSpecificOutput\":{\"permissionDecision\":\"deny\"},\"systemMessage\":\"[guard-outline-before-prose] 缺少合约文件和细纲文件: 需要 .story-system/contracts/chapter_${CHAPTER_NUM}.contract.md 或 大纲/细纲_第${CHAPTER_NUM}章.md。请先创建对应合约或细纲再写正文。\"}" >&2
exit 2
