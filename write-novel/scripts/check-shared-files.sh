#!/bin/bash
# check-shared-files.sh — 检查跨 skill 同名文件内容一致性（移植自 oh-story-claudecode，适配 write-novel）
# 扫描所有 skill 的 references/ 与 scripts/ 目录，找出同名文件并比较内容
# 兼容 bash 3+（macOS）
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

SKILLS_DIR="$PLUGIN_ROOT/skills"

# 已知有意差异（basename）：这些文件被允许在各 skill 间不同
# - output-templates.md / material-decomposition.md：每个 skill 拥有自己的输出/拆解 schema
# - quality-checklist.md：各 skill 的检查清单不同
# - genre-* 文件：拆文 skill（write-novel-short-analyze）会前置「用作拆文标尺时」分析镜头头，writer skill 没有
# - female-audience-writing.md：长篇/短篇女频写法不同，有意分叉
# - state-tracking.md：long-write（卷级伏笔+功法状态）/ import（逆向提取）/ short-write（轻量）追踪粒度不同，无 sync-source，有意分叉
IGNORE_NAMES="output-templates.md material-decomposition.md quality-checklist.md \
genre-catalog.md genre-core-mechanics.md genre-readers.md \
genre-writing-formulas.md genre-writing-techniques.md female-audience-writing.md \
state-tracking.md"

# 分析镜头分叉（basename）：write-novel-short-analyze 的副本有意前置分析镜头头，从比较集中剔除；
# 其余副本（writer skill + agent-references）仍须逐字节一致。
ANALYST_DIVERGENT_NAMES="character-basics.md character-design-methods.md character-relations.md"

mismatches=0
checked=0

echo "Shared File Consistency Check (write-novel)"
echo "============================================="

dup_names="$(find "$SKILLS_DIR" -type f -path '*/references/*' ! -name '.gitkeep' -exec basename {} \; 2>/dev/null | sort | uniq -d)"

for base in $dup_names; do
  skip=false
  for ignore in $IGNORE_NAMES; do
    if [ "$base" = "$ignore" ]; then
      skip=true
      break
    fi
  done
  if [ "$skip" = true ]; then
    continue
  fi
  paths=()
  while IFS= read -r fpath; do
    [ -z "$fpath" ] && continue
    paths+=("$fpath")
  done < <(find "$SKILLS_DIR" -type f -path '*/references/*' -name "$base" 2>/dev/null)

  case " $ANALYST_DIVERGENT_NAMES " in
    *" $base "*)
      filtered=()
      for p in ${paths[@]+"${paths[@]}"}; do
        case "$p" in
          */write-novel-short-analyze/*) ;;
          *) filtered+=("$p") ;;
        esac
      done
      paths=(${filtered[@]+"${filtered[@]}"})
      ;;
  esac

  if [ ${#paths[@]} -lt 2 ]; then
    continue
  fi

  checked=$((checked + 1))
  ref_path="${paths[0]}"
  ref_skill="$(echo "$ref_path" | sed "s|$SKILLS_DIR/||" | cut -d'/' -f1)"
  all_match=true

  for ((i = 1; i < ${#paths[@]}; i++)); do
    if ! diff -q "$ref_path" "${paths[$i]}" >/dev/null 2>&1; then
      skill_name="$(echo "${paths[$i]}" | sed "s|$SKILLS_DIR/||" | cut -d'/' -f1)"
      if [ "$all_match" = true ]; then
        echo ""
        echo "MISMATCH: $base"
        echo "  Reference: $ref_skill"
      fi
      echo "  Differs in: $skill_name"
      all_match=false
      mismatches=$((mismatches + 1))
    fi
  done
done

# scripts/ 同名副本也按受管副本要求逐字节一致
script_dup_names="$(find "$SKILLS_DIR" -type f -path '*/scripts/*' ! -name '.gitkeep' -exec basename {} \; 2>/dev/null | sort | uniq -d)"

for base in $script_dup_names; do
  paths=()
  while IFS= read -r fpath; do
    [ -z "$fpath" ] && continue
    paths+=("$fpath")
  done < <(find "$SKILLS_DIR" -type f -path '*/scripts/*' -name "$base" 2>/dev/null)

  if [ ${#paths[@]} -lt 2 ]; then
    continue
  fi

  checked=$((checked + 1))
  ref_path="${paths[0]}"
  ref_skill="$(echo "$ref_path" | sed "s|$SKILLS_DIR/||" | cut -d'/' -f1)"
  all_match=true

  for ((i = 1; i < ${#paths[@]}; i++)); do
    if ! diff -q "$ref_path" "${paths[$i]}" >/dev/null 2>&1; then
      skill_name="$(echo "${paths[$i]}" | sed "s|$SKILLS_DIR/||" | cut -d'/' -f1)"
      if [ "$all_match" = true ]; then
        echo ""
        echo "MISMATCH: $base"
        echo "  Reference: $ref_skill"
      fi
      echo "  Differs in: $skill_name"
      all_match=false
      mismatches=$((mismatches + 1))
    fi
  done
done

echo ""
echo "============================================="
echo "Files checked (shared): $checked | Mismatches: $mismatches"

# ============================================================
# 新增校验模式：指针文件 + 共享源 + 版本指纹 + 命名空间
# ============================================================

SHARED_DIR="$PLUGIN_ROOT/references/shared"
MANIFEST="$SHARED_DIR/MANIFEST.yaml"

# 11.1 指针文件验证：识别 `> **共享参考文件**` 首行，提取版本指纹，验证共享源存在
echo ""
echo "--- Pointer File Validation ---"
pointer_errors=0
pointer_checked=0

while IFS= read -r ptr; do
  [ -z "$ptr" ] && continue
  pointer_checked=$((pointer_checked + 1))
  first_line="$(head -1 "$ptr" 2>/dev/null)"
  if [[ "$first_line" != *"*共享参考文件*"* ]]; then
    continue
  fi
  # 提取共享源路径
  shared_src_line="$(grep -m1 '共享源：' "$ptr" 2>/dev/null)"
  shared_src_path="${shared_src_line#*共享源：}"
  shared_src_path="$(echo "$shared_src_path" | tr -d '[:space:]')"
  if [ -z "$shared_src_path" ]; then
    echo "  [FAIL] $ptr: 缺少共享源字段"
    pointer_errors=$((pointer_errors + 1))
    continue
  fi
  # 解析为绝对路径：相对 PLUGIN_ROOT
  abs_src="$PLUGIN_ROOT/$shared_src_path"
  if [ ! -f "$abs_src" ]; then
    echo "  [FAIL] $ptr: 共享源不存在 $shared_src_path"
    pointer_errors=$((pointer_errors + 1))
    continue
  fi
  # 提取版本指纹
  version_line="$(grep -m1 '版本指纹：' "$ptr" 2>/dev/null)"
  version="${version_line#*版本指纹：}"
  version="$(echo "$version" | tr -d '[:space:]')"
  if [ -z "$version" ]; then
    echo "  [WARN] $ptr: 缺少版本指纹"
  fi
done < <(find "$SKILLS_DIR" -type f -name '*.md' -path '*/references/*' 2>/dev/null)

echo "Pointer files checked: $pointer_checked | Errors: $pointer_errors"

# 11.2 新副本阻断：白名单中的文件必须是指针格式，不得为实体副本
echo ""
echo "--- Whitelist Enforcement ---"
whitelist_errors=0
whitelist_checked=0

if [ -f "$MANIFEST" ]; then
  # 从 MANIFEST.yaml 提取 shared_sources 下的文件名
  shared_names="$(awk '/^shared_sources:/,/^whitelist_real_files:/' "$MANIFEST" | grep -E '^  [a-z].*\.md:' | sed 's/^  //' | sed 's/:$//')"
  for name in $shared_names; do
    # 找到所有同名文件
    while IFS= read -r fpath; do
      [ -z "$fpath" ] && continue
      whitelist_checked=$((whitelist_checked + 1))
      first_line="$(head -1 "$fpath" 2>/dev/null)"
      if [[ "$first_line" != *"*共享参考文件*"* ]]; then
        echo "  [FAIL] $fpath: 在共享白名单中但不是指针文件（应为指针格式）"
        whitelist_errors=$((whitelist_errors + 1))
      fi
    done < <(find "$SKILLS_DIR" -type f -name "$name" -path '*/references/*' 2>/dev/null)
  done
fi

echo "Whitelist files checked: $whitelist_checked | Errors: $whitelist_errors"

# 11.4 命名空间校验：拒绝 skills/story-* 目录；拒绝 agents/ 裸名 agent
echo ""
echo "--- Namespace Validation ---"
namespace_errors=0

# skills/ 下不应有 story-* 目录
for d in "$SKILLS_DIR"/story-*; do
  if [ -d "$d" ]; then
    echo "  [FAIL] 旧命名 skill 目录存在: $d（应迁移为 write-novel-*）"
    namespace_errors=$((namespace_errors + 1))
  fi
done

# agents/ 下不应有裸名 agent 文件
AGENTS_DIR="$PLUGIN_ROOT/agents"
BARE_AGENT_NAMES="narrative-writer reviewer character-designer consistency-checker deconstruction-agent chapter-extractor story-architect story-explorer story-researcher"
for name in $BARE_AGENT_NAMES; do
  if [ -f "$AGENTS_DIR/$name.md" ]; then
    echo "  [FAIL] 裸名 agent 文件存在: $AGENTS_DIR/$name.md（应迁移为 write-novel-$name.md）"
    namespace_errors=$((namespace_errors + 1))
  fi
done

# 代码中不应有 subagent_type: "裸名" 调用
bare_refs="$(grep -rn 'subagent_type: "narrative-writer"\|subagent_type: "reviewer"\|subagent_type: "character-designer"\|subagent_type: "consistency-checker"\|subagent_type: "deconstruction-agent"\|subagent_type: "chapter-extractor"\|subagent_type: "story-architect"\|subagent_type: "story-explorer"\|subagent_type: "story-researcher"' "$SKILLS_DIR" "$AGENTS_DIR" 2>/dev/null | wc -l | tr -d ' ' || true)"
if [ "$bare_refs" -gt 0 ]; then
  echo "  [FAIL] 发现 $bare_refs 处裸名 subagent_type 调用（应加 write-novel- 前缀）"
  namespace_errors=$((namespace_errors + 1))
fi

echo "Namespace errors: $namespace_errors"

# 11.5 部署态一致性：.claude/skills/ 不应同时存在 story-* 和 write-novel-* 同语义目录
echo ""
echo "--- Deploy State Validation ---"
deploy_errors=0
# 本校验仅对已部署项目生效（检查项目根 .claude/）
PROJECT_CLAUDE_DIR="$REPO_ROOT/.claude"
if [ -d "$PROJECT_CLAUDE_DIR/skills" ]; then
  for d in "$PROJECT_CLAUDE_DIR/skills"/story-*; do
    if [ -d "$d" ]; then
      base="${d##*/story-}"
      if [ -d "$PROJECT_CLAUDE_DIR/skills/write-novel-$base" ]; then
        echo "  [FAIL] 部署态新旧并存: story-$base 和 write-novel-$base 同时存在"
        deploy_errors=$((deploy_errors + 1))
      fi
    fi
  done
fi
echo "Deploy state errors: $deploy_errors"

# 汇总
total_errors=$((mismatches + pointer_errors + whitelist_errors + namespace_errors + deploy_errors))

echo ""
echo "============================================="
echo "Total errors: $total_errors"

if [ "$total_errors" -gt 0 ]; then
  echo ""
  echo "NOTE: Some mismatches may be intentional (skill-specific customizations)."
  echo "      Review each case before syncing."
  exit 1
fi

echo "All shared files are consistent."
