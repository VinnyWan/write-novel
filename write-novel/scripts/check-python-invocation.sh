#!/bin/bash
# check-python-invocation.sh — 守卫：技能文档与 hooks 里禁止裸调 `python3`（移植自 oh-story）
#
# Windows 上 python.org 安装后 `python3` 会落到 Microsoft Store 占位程序、以 exit 49
# 静默失败。所有调用必须先按 python3 -> python -> py 探测可用解释器：
#   for PYBIN in python3 python py; do "$PYBIN" -c "" 2>/dev/null && break; done
#   "$PYBIN" -c "..."
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [ -z "$REPO_ROOT" ]; then
  echo "Error: not in a git repository"
  exit 1
fi

PLUGIN_ROOT=""
for cand in "$REPO_ROOT" "$REPO_ROOT/write-novel"; do
  if [ -d "$cand/skills" ] && [ -d "$cand/agents" ]; then
    PLUGIN_ROOT="$cand"
    break
  fi
done
if [ -z "$PLUGIN_ROOT" ]; then
  echo "Error: plugin root not found"
  exit 1
fi

# 裸调用形态：python3 + 空白 + 任意非空白参数（覆盖 -c / -m / << / 脚本路径 / 引号）
PATTERN='python3[[:space:]]+[^[:space:]]'
ALLOW='python3 python py'

echo "Python Invocation Guard (write-novel)"
echo "======================================="

# skills/ 文档 + hooks 配置（CI scripts 自身允许用任意写法，不扫）
hits=""
for target in "$PLUGIN_ROOT/skills" "$PLUGIN_ROOT/hooks"; do
  [ -d "$target" ] || continue
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    hits="${hits}${line}
"
  done < <(grep -rnE "$PATTERN" "$target" 2>/dev/null | grep -vF "$ALLOW" || true)
done

if [ -n "$hits" ]; then
  echo "FAIL: 发现裸调 python3（Windows 上会 exit 49）："
  echo "$hits"
  echo
  echo "改用解释器探测形态："
  echo '  for PYBIN in python3 python py; do "$PYBIN" -c "" 2>/dev/null && break; done'
  echo '  "$PYBIN" -c "..."'
  exit 1
fi

echo "OK: 未发现裸调 python3"
