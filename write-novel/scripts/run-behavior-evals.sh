#!/bin/bash
# run-behavior-evals.sh — write-novel 行为 eval 运行器（bash wrapper → python 实现）
# 读取 evals/fixtures/behavior/fast.json，逐 case 执行结构化/grep 断言，输出 pass/fail。
# 退出码：0 全绿，1 有失败。
# python 在此用作确定性数据处理工具（解析 JSON + 调度检查），符合 CLAUDE.md「编码处理等底层确定性工具」豁免。

set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [ -z "$REPO_ROOT" ]; then
  echo "Error: not in a git repository" >&2
  exit 2
fi

PLUGIN_ROOT=""
for cand in "$REPO_ROOT" "$REPO_ROOT/write-novel"; do
  if [ -d "$cand/skills" ] && [ -d "$cand/agents" ]; then
    PLUGIN_ROOT="$cand"
    break
  fi
done
if [ -z "$PLUGIN_ROOT" ]; then
  echo "Error: cannot locate plugin root (skills/ + agents/)" >&2
  exit 2
fi

PYBIN=""
for cand in python3 python py; do
  if command -v "$cand" >/dev/null 2>&1; then PYBIN="$(command -v "$cand")"; break; fi
done
if [ -z "$PYBIN" ]; then
  echo "Error: no python interpreter found" >&2
  exit 2
fi

exec "$PYBIN" "$PLUGIN_ROOT/scripts/run_behavior_evals.py" "$PLUGIN_ROOT"
