#!/bin/bash
# check-repo-hygiene.sh — 仓库卫生护栏
# 校验依赖目录 / 构建产物 / 缓存目录未被 Git 跟踪，且 .gitignore 覆盖这些模式。
# 实现 repo-hygiene-guard 不变量。兼容 bash 3+（macOS）。
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [ -z "$REPO_ROOT" ]; then
  echo "Error: not in a git repository"
  exit 1
fi
cd "$REPO_ROOT"

echo "Repo Hygiene Check"
echo "============================================="

errors=0

# 1. 不得跟踪的产物模式
PATTERNS="node_modules/ dist/ __pycache__/ .pytest_cache/"
for pat in $PATTERNS; do
  count="$(git ls-files | grep -c "$pat" || true)"
  if [ "$count" -gt 0 ]; then
    echo "  [FAIL] Git 仍跟踪 $count 个 '$pat' 路径（应取消跟踪：git rm -r --cached）"
    git ls-files | grep "$pat" | head -3 | sed 's/^/         e.g. /'
    errors=$((errors + 1))
  else
    echo "  [OK]   '$pat' 未被跟踪"
  fi
done

# 2. .gitignore 必须覆盖这些模式
GITIGNORE="$REPO_ROOT/.gitignore"
for pat in $PATTERNS; do
  if [ -f "$GITIGNORE" ] && grep -qF "$pat" "$GITIGNORE"; then
    :
  else
    echo "  [FAIL] .gitignore 缺少模式 '$pat'"
    errors=$((errors + 1))
  fi
done

echo ""
echo "============================================="
if [ "$errors" -gt 0 ]; then
  echo "Repo hygiene errors: $errors"
  exit 1
fi
echo "[PASS] repo hygiene clean — 无依赖/构建/缓存产物被跟踪"
