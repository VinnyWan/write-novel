#!/bin/bash
# guard-outline-before-prose.sh — 正文写入前强制检查对应细纲是否存在
# 阻断式 hook：无对应细纲时拒绝正文首次写入
# 触发条件：Write/Edit 工具，目标为 正文/ 目录下的 .md 文件
set -euo pipefail

# This hook is triggered before Write/Edit on 正文/ files.
# stdin: JSON payload with file_path info
# Exit 2 → deny; Exit 0 → allow

source "$(dirname "$0")/lib/common.sh"

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python3 -c "
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

# Check if outline file exists
OUTLINE_FILE="$BOOK_DIR/大纲/细纲_第${CHAPTER_NUM}章.md"

if [ -f "$OUTLINE_FILE" ]; then
    exit 0
fi

# Block: no outline file
echo "{\"hookSpecificOutput\":{\"permissionDecision\":\"deny\"},\"systemMessage\":\"[guard-outline-before-prose] 缺少细纲文件: 大纲/细纲_第${CHAPTER_NUM}章.md。请先创建对应细纲再写正文。\"}" >&2
exit 2
