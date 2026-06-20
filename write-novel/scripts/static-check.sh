#!/bin/bash
# static-check.sh — Skill 结构与路径完整性检查（移植自 oh-story-claudecode，适配 write-novel）
# 检查：frontmatter、引用路径有效、死文件、交叉引用、Agent 引用有效、
#       反引号引用有效(含 skill 作用域)、裸文件名检测、SKILL.md section 引用
#
# 解析规则（write-novel 适配）：每个 skill 自带 references/ 目录，链接相对该目录解析；
# 跨 skill 形式 story-X/references/Y 相对插件根解析；部署根 references/methodology|shared 作回退。

set -euo pipefail

# 定位插件根：write-novel 插件位于仓库子目录 write-novel/，含 skills/ + agents/ + references/
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
  echo "Error: plugin root (with skills/ + agents/) not found under $REPO_ROOT"
  exit 1
fi

SKILLS_DIR="$PLUGIN_ROOT/skills"
REFERENCES_ROOT="$PLUGIN_ROOT/references"
AGENTS_DIR="$PLUGIN_ROOT/agents"

TOTAL=0
PASS=0
FAIL=0
WARN=0

# ---------- helpers ----------

extract_referenced_paths() {
  local file="$1"
  grep -oE '\]\([^)]+\)' "$file" 2>/dev/null | sed 's/](\(.*\))/\1/' | grep -v '^http' | grep -v '^#' || true
  grep -oE '(references|scripts|assets)/[^ `")\]]+' "$file" 2>/dev/null || true
}

extract_agent_refs() {
  local file="$1"
  grep -oE 'subagent_type:[[:space:]]*"[^"]+"' "$file" 2>/dev/null | sed 's/subagent_type:[[:space:]]*"//' | sed 's/"$//' || true
  grep -oE 'subagent_type="[^"]+"' "$file" 2>/dev/null | sed 's/subagent_type="//' | sed 's/"//' || true
  grep -oE '\(subagent_type:[[:space:]]*[a-z][a-z0-9_-]+\)' "$file" 2>/dev/null | sed 's/(subagent_type:[[:space:]]*//' | sed 's/)$//' || true
}

# 三级解析：判定 references 链接是否有效
# $1=skill_dir $2=link  返回 0=有效 1=无效
resolve_ref() {
  local skill_dir="$1" link="$2"
  local base="${link##*/}"
  # 1. skill-local: skills/<skill>/<link>
  if [ -e "$skill_dir/$link" ]; then return 0; fi
  # 2. 跨 skill / 插件根形式（link 已含 write-novel-X/ 或 story-X/ 或 references/ 前缀）：相对插件根
  if [ -e "$PLUGIN_ROOT/$link" ]; then return 0; fi
  # 3. 部署根回退
  if [ -f "$REFERENCES_ROOT/methodology/$base" ]; then return 0; fi
  if [ -f "$REFERENCES_ROOT/shared/$base" ]; then return 0; fi
  if [ -f "$REFERENCES_ROOT/$base" ]; then return 0; fi
  return 1
}

# ---------- checks ----------

check_skill() {
  local skill_dir="$1"
  local skill_name
  skill_name="$(basename "$skill_dir")"
  local skill_file="$skill_dir/SKILL.md"

  if [ ! -f "$skill_file" ]; then
    return
  fi

  TOTAL=$((TOTAL + 1))
  local errors=0
  local warnings=0

  echo ""
  echo "--- $skill_name ---"

  # Check 1: frontmatter (name + description required)
  local has_name has_desc
  has_name="$(grep -c '^name:' "$skill_file" || true)"
  has_desc="$(grep -c '^description:' "$skill_file" || true)"
  if [ "$has_name" -ge 1 ] && [ "$has_desc" -ge 1 ]; then
    echo "  [PASS] frontmatter: name + description present"
  else
    echo "  [FAIL] frontmatter: missing name or description"
    errors=$((errors + 1))
  fi

  # Check 2: referenced paths exist (三级解析)
  local broken_paths=()
  while IFS= read -r ref_path; do
    [ -z "$ref_path" ] && continue
    # 仅检查 references/ scripts/ assets/ 开头的路径
    case "$ref_path" in
      references/*|scripts/*|assets/*|write-novel-*/references/*|story-*/references/*) ;;
      *) continue ;;
    esac
    if ! resolve_ref "$skill_dir" "$ref_path"; then
      broken_paths+=("$ref_path")
    fi
  done < <(extract_referenced_paths "$skill_file" | sort -u)

  if [ ${#broken_paths[@]} -eq 0 ]; then
    echo "  [PASS] all referenced paths exist"
  else
    echo "  [FAIL] broken path references:"
    for p in "${broken_paths[@]}"; do
      echo "         -> $p"
    done
    errors=$((errors + 1))
  fi

  # Check 3: dead files in references/ (recursive, skip .gitkeep)
  if [ -d "$skill_dir/references" ]; then
    local dead_files=()
    while IFS= read -r -d '' ref_file; do
      local ref_basename
      ref_basename="$(basename "$ref_file")"
      [ "$ref_basename" = ".gitkeep" ] && continue
      if ! grep -qF "$ref_basename" "$skill_file" 2>/dev/null; then
        local parent_covered=false
        local check_dir="$(dirname "$ref_file")"
        while [ "$check_dir" != "$skill_dir" ] && [ "$check_dir" != "/" ]; do
          local rel_dir="${check_dir#$skill_dir/}/"
          if grep -qF "$rel_dir" "$skill_file" 2>/dev/null; then
            parent_covered=true
            break
          fi
          check_dir="$(dirname "$check_dir")"
        done
        if [ "$parent_covered" = false ]; then
          local rel_path="${ref_file#$skill_dir/}"
          dead_files+=("$rel_path")
        fi
      fi
    done < <(find "$skill_dir/references" -type f -print0 2>/dev/null)

    if [ ${#dead_files[@]} -eq 0 ]; then
      echo "  [PASS] no dead files in references/"
    else
      echo "  [WARN] files in references/ not referenced in SKILL.md:"
      for f in "${dead_files[@]}"; do
        echo "         -> $f"
      done
      warnings=$((warnings + 1))
    fi
  fi

  # Check 4: Internal cross-references in references/ files
  if [ -d "$skill_dir/references" ]; then
    local broken_xrefs=()
    while IFS= read -r -d '' ref_file; do
      [ "$(basename "$ref_file")" = ".gitkeep" ] && continue
      while IFS= read -r xref; do
        [ -z "$xref" ] && continue
        [[ "$xref" == http* ]] && continue
        [[ "$xref" == \#* ]] && continue
        [[ "$xref" == *"{"* ]] && continue
        local xref_full="$(dirname "$ref_file")/$xref"
        if [ ! -e "$xref_full" ]; then
          broken_xrefs+=("$(basename "$ref_file") -> $xref")
        fi
      done < <(grep -oE '\]\([^)]+\)' "$ref_file" 2>/dev/null | sed 's/](\(.*\))/\1/' | grep -v '^http' | grep -v '^#' || true)
    done < <(find "$skill_dir/references" -type f -name "*.md" -print0 2>/dev/null)

    if [ ${#broken_xrefs[@]} -eq 0 ]; then
      echo "  [PASS] no broken cross-references in references/"
    else
      echo "  [FAIL] broken cross-references in references/:"
      for x in "${broken_xrefs[@]}"; do
        echo "         -> $x"
      done
      errors=$((errors + 1))
    fi
  fi

  # Check 5: Agent references valid (对照部署模板 + 规范 agents/)
  local agent_names=()
  if [ -d "$AGENTS_DIR" ]; then
    for f in "$AGENTS_DIR/"*.md; do
      [ -f "$f" ] && agent_names+=("$(basename "$f" .md)")
    done
  fi

  local broken_agents=()
  while IFS= read -r agent_ref; do
    [ -z "$agent_ref" ] && continue
    local found=false
    for name in "${agent_names[@]}"; do
      if [ "$agent_ref" = "$name" ]; then
        found=true
        break
      fi
    done
    if [ "$found" = false ]; then
      broken_agents+=("$agent_ref")
    fi
  done < <(extract_agent_refs "$skill_file" | sort -u)

  if [ ${#broken_agents[@]} -eq 0 ]; then
    if [ ${#agent_names[@]} -gt 0 ] && [ -n "$(extract_agent_refs "$skill_file")" ]; then
      echo "  [PASS] all agent references valid"
    fi
  else
    echo "  [FAIL] unknown agent references:"
    for a in "${broken_agents[@]}"; do
      echo "         -> $a"
    done
    errors=$((errors + 1))
  fi

  # Check 6: Backtick-wrapped inline file references
  local broken_inline=()
  while IFS= read -r -d '' src_file; do
    local src_rel="${src_file#$skill_dir/}"
    while IFS= read -r ref_name; do
      [ -z "$ref_name" ] && continue
      [[ "$ref_name" == *"{"* ]] && continue
      [[ "$ref_name" =~ [^[:ascii:]] ]] && continue
      local base_name="$(basename "$ref_name")"
      [[ "$base_name" =~ ^[a-z0-9_-]+\.md$ ]] || continue
      [[ "$base_name" =~ ^_ ]] && continue
      local found=false
      local is_scoped_ref=false
      local src_parent="$(basename "$(dirname "$src_file")")"
      [[ "$src_parent" == "references" ]] && [[ "$ref_name" != */* ]] && is_scoped_ref=true
      # 跳过运行态项目路径（写作时创建，非插件源文件）：追踪/ 设定/ 大纲/ 正文/ 对标/ 拆文库/ 参考资料/ .story-system/
      if [[ "$ref_name" == 追踪/* || "$ref_name" == 设定/* || "$ref_name" == 大纲/* || "$ref_name" == 正文/* || "$ref_name" == 对标/* || "$ref_name" == 拆文库/* || "$ref_name" == 参考资料/* || "$ref_name" == .story-system/* ]]; then
        continue
      fi
      local ref_dir="$(dirname "$src_file")"
      if [ -f "$ref_dir/$ref_name" ]; then
        found=true
      elif find "$skill_dir" -type f -name "$base_name" -print -quit 2>/dev/null | grep -q .; then
        found=true
      elif [ "$is_scoped_ref" = false ] && find "$SKILLS_DIR" -type f -name "$base_name" -print -quit 2>/dev/null | grep -q .; then
        found=true
      elif [ "$is_scoped_ref" = false ] && [ -f "$PLUGIN_ROOT/$ref_name" ]; then
        found=true
      fi
      if [ "$found" = false ]; then
        broken_inline+=("$src_rel -> $ref_name")
      fi
    done < <(grep -oE '`[^`]+\.md`' "$src_file" 2>/dev/null | sed 's/`//g' | sort -u || true)
  done < <(find "$skill_dir" -type f -name "*.md" -print0 2>/dev/null)

  if [ ${#broken_inline[@]} -eq 0 ]; then
    echo "  [PASS] no broken inline file references"
  else
    echo "  [FAIL] broken inline file references (backtick-wrapped):"
    for x in "${broken_inline[@]}"; do
      echo "         -> $x"
    done
    errors=$((errors + 1))
  fi

  # Check 7: Bare prose .md filename detection
  local bare_refs=()
  while IFS= read -r -d '' src_file; do
    local src_rel="${src_file#$skill_dir/}"
    while IFS= read -r bare; do
      [ -z "$bare" ] && continue
      local bname
      bname="$(basename "$bare")"
      [[ "$bname" =~ ^[a-z0-9_-]+\.md$ ]] || continue
      [[ "$bname" =~ ^_ ]] && continue
      [[ "$bname" =~ ^[a-z]+[0-9]+\.md$ ]] && continue
      bare_refs+=("$src_rel: $bname")
    done < <(awk '
      /^```/ { in_block = !in_block; next }
      in_block { next }
      { gsub(/\[[^\]]*\]\([^)]*\)/, "")
        gsub(/`[^`]*`/, "")
        while (match($0, /[a-z0-9_-]+\.md/)) {
          print substr($0, RSTART, RLENGTH)
          $0 = substr($0, RSTART + RLENGTH)
        }
      }
    ' "$src_file" 2>/dev/null || true)
  done < <(find "$skill_dir" -type f -name "*.md" -print0 2>/dev/null)

  local unique_bare=()
  if [ ${#bare_refs[@]} -gt 0 ]; then
    while IFS= read -r ref; do
      unique_bare+=("$ref")
    done < <(printf '%s\n' "${bare_refs[@]}" | sort -u)
  fi

  local broken_bare=()
  local valid_bare=()
  # 运行态文件名（写作时创建于 追踪/ 等，非插件源文件），跳过裸名检测
  local runtime_bare="run-ledger.md state.md context.md characters.md foreshadowing.md progress.md"
  for x in ${unique_bare[@]+"${unique_bare[@]}"}; do
    local bname="${x##* }"
    local skip_runtime=false
    for rb in $runtime_bare; do
      if [ "$bname" = "$rb" ]; then skip_runtime=true; break; fi
    done
    if [ "$skip_runtime" = true ]; then
      continue
    fi
    local src_part="${x%%: *}"
    local src_file_path="$skill_dir/$src_part"
    local found=false
    local ref_dir="$(dirname "$src_file_path")"
    if [ -f "$ref_dir/$bname" ]; then
      found=true
    elif find "$skill_dir" -type f -name "$bname" -print -quit 2>/dev/null | grep -q .; then
      found=true
    elif find "$SKILLS_DIR" -type f -name "$bname" -print -quit 2>/dev/null | grep -q .; then
      found=true
    elif [ -f "$REFERENCES_ROOT/methodology/$bname" ] || [ -f "$REFERENCES_ROOT/shared/$bname" ]; then
      found=true
    fi
    if [ "$found" = false ]; then
      broken_bare+=("$x")
    else
      valid_bare+=("$x")
    fi
  done

  if [ ${#broken_bare[@]} -gt 0 ]; then
    echo "  [FAIL] bare .md filenames referencing non-existent files:"
    for x in "${broken_bare[@]}"; do
      echo "         -> $x"
    done
    errors=$((errors + 1))
  fi
  if [ ${#valid_bare[@]} -gt 0 ]; then
    echo "  [WARN] bare .md filenames not wrapped in backticks:"
    for x in "${valid_bare[@]}"; do
      echo "         -> $x"
    done
    warnings=$((warnings + 1))
  fi
  if [ ${#broken_bare[@]} -eq 0 ] && [ ${#valid_bare[@]} -eq 0 ]; then
    echo "  [PASS] no bare prose .md filename references"
  fi

  # Check 8: SKILL.md section reference validation
  local broken_section_refs=()
  if [ -f "$skill_dir/SKILL.md" ] && [ -d "$skill_dir/references" ]; then
    local headings=()
    local h_tmp
    h_tmp="$(grep -E '^#{1,4}[[:space:]]' "$skill_dir/SKILL.md" 2>/dev/null | sed -E 's/^#+[[:space:]]*//' | sed 's/[[:space:]]*$//' | tr '[:upper:]' '[:lower:]')" || true
    if [ -n "$h_tmp" ]; then
      while IFS= read -r h_line; do
        headings+=("$h_line")
      done <<< "$h_tmp"
    fi

    while IFS= read -r -d '' src_file; do
      local src_rel="${src_file#$skill_dir/}"
      local refs_tmp
      refs_tmp="$(grep 'SKILL\.md' "$src_file" 2>/dev/null | grep -oE '(见|参考|参见|详见) SKILL\.md [^)]+' | sed -E 's/^(见|参考|参见|详见) SKILL\.md //' | sort -u)" || true
      [ -z "$refs_tmp" ] && continue
      while IFS= read -r ref_text; do
        [ -z "$ref_text" ] && continue
        local clean_ref
        clean_ref="$(echo "$ref_text" | sed -E 's/[）)」』,，。；：;:]+$//' | sed -E 's/[[:space:]]*$//' | tr '[:upper:]' '[:lower:]')"
        [ -z "$clean_ref" ] && continue
        local matched=false
        for h in "${headings[@]}"; do
          if [[ "$h" == *"$clean_ref"* ]] || [[ "$clean_ref" == *"$h"* ]]; then
            matched=true
            break
          fi
        done
        if [ "$matched" = false ]; then
          local prefix="$clean_ref"
          while [[ "$prefix" == *[[:space:]]* ]]; do
            prefix="${prefix% *}"
            [ -z "$prefix" ] && break
            for h in "${headings[@]}"; do
              if [[ "$h" == *"$prefix"* ]] || [[ "$prefix" == *"$h"* ]]; then
                matched=true
                break 2
              fi
            done
          done
          if [ "$matched" = false ] && [ -n "$prefix" ]; then
            for _cnt in 1 2 3; do
              prefix="${prefix%?}"
              [ -z "$prefix" ] && break
              for h in "${headings[@]}"; do
                if [[ "$h" == *"$prefix"* ]] || [[ "$prefix" == *"$h"* ]]; then
                  matched=true
                  break 2
                fi
              done
            done
          fi
        fi
        if [ "$matched" = false ]; then
          broken_section_refs+=("$src_rel -> SKILL.md '$ref_text'")
        fi
      done <<< "$refs_tmp"
    done < <(find "$skill_dir/references" -maxdepth 1 -type f -name "*.md" -print0 2>/dev/null)
  fi

  if [ ${#broken_section_refs[@]} -eq 0 ]; then
    echo "  [PASS] no broken SKILL.md section references"
  else
    echo "  [FAIL] broken SKILL.md section references:"
    for x in "${broken_section_refs[@]}"; do
      echo "         -> $x"
    done
    errors=$((errors + 1))
  fi

  if [ "$errors" -eq 0 ]; then
    PASS=$((PASS + 1))
    if [ "$warnings" -gt 0 ]; then
      WARN=$((WARN + 1))
      echo "  Result: PASS ($warnings warnings)"
    else
      echo "  Result: PASS"
    fi
  else
    FAIL=$((FAIL + 1))
    echo "  Result: FAIL ($errors errors, $warnings warnings)"
  fi
}

# ---------- main ----------

echo "Skill Static Check (write-novel)"
echo "================================="
echo "Plugin: $PLUGIN_ROOT"

for skill_dir in "$SKILLS_DIR"/*/; do
  check_skill "$skill_dir"
done

echo ""
echo "================================="
echo "Total: $TOTAL | Pass: $PASS | Fail: $FAIL | Warn: $WARN"

if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
