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
      # Also accept write-novel: namespaced form (plugin-level spawn)
      [ -f "$f" ] && agent_names+=("write-novel:$(basename "$f" .md)")
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

  # Check 9: 外移引用完整性——SKILL.md 引用的 references/<流程文件>.md 必须存在且非空
  # 仅检查本地 markdown 链接 (references/X.md) 与反引号路径 `references/X.md`
  # 路径解析走三级：skill-local → 插件根 → 部署根 methodology/shared 回退
  # 防止瘦身后指针指向空文件或不存在文件
  local broken_external=()
  local any_external=false
  while IFS= read -r ext_ref; do
    [ -z "$ext_ref" ] && continue
    any_external=true
    local ext_base="${ext_ref##*/}"
    local ext_path="$skill_dir/$ext_ref"
    # 三级解析定位真实文件
    local resolved=""
    if [ -f "$ext_path" ]; then
      resolved="$ext_path"
    elif [ -f "$PLUGIN_ROOT/$ext_ref" ]; then
      resolved="$PLUGIN_ROOT/$ext_ref"
    elif [ -f "$REFERENCES_ROOT/methodology/$ext_base" ]; then
      resolved="$REFERENCES_ROOT/methodology/$ext_base"
    elif [ -f "$REFERENCES_ROOT/shared/$ext_base" ]; then
      resolved="$REFERENCES_ROOT/shared/$ext_base"
    elif [ -f "$REFERENCES_ROOT/$ext_base" ]; then
      resolved="$REFERENCES_ROOT/$ext_base"
    fi
    if [ -z "$resolved" ]; then
      broken_external+=("$ext_ref (不存在)")
    elif [ ! -s "$resolved" ]; then
      broken_external+=("$ext_ref (空文件)")
    elif [ "$(grep -c '.' "$resolved")" -eq 0 ]; then
      broken_external+=("$ext_ref (无有效内容)")
    fi
  done < <({ grep -oE '\]\(references/[A-Za-z0-9_/.-]+\.md\)' "$skill_file" 2>/dev/null | sed 's/](//; s/)$//'; grep -oE '`references/[A-Za-z0-9_/.-]+\.md`' "$skill_file" 2>/dev/null | tr -d '`'; } | sort -u)

  if [ ${#broken_external[@]} -eq 0 ]; then
    if [ "$any_external" = true ]; then
      echo "  [PASS] externalized reference files exist and non-empty"
    fi
  else
    echo "  [FAIL] broken externalized reference files:"
    for x in "${broken_external[@]}"; do
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

# ---------- shared references integrity (跨 skill 顶层检查) ----------
# Check 10: references/shared/ 内 wikilink [[...]] 与路径引用 ](...) 的悬空检测
# 只校验「引用目标是否存在」，不校验「文件是否被消费」（引用计数），
# 以免误伤 contract-schema（仅 eval 引用）、pattern-schema（仅 agent 引用）等合法低频文件。
check_shared_references() {
  local shared_dir="$REFERENCES_ROOT/shared"
  TOTAL=$((TOTAL + 1))
  echo ""
  echo "--- references/shared (跨 skill) ---"
  if [ ! -d "$shared_dir" ]; then
    echo "  [SKIP] references/shared/ 不存在"
    PASS=$((PASS + 1))
    return
  fi

  local errors=0
  local broken=()
  local any_ref=false
  while IFS= read -r -d '' ref_file; do
    [ "$(basename "$ref_file")" = ".gitkeep" ] && continue
    local ref_dir
    ref_dir="$(dirname "$ref_file")"
    # 1) wikilink [[name]] 或 [[path/to/name]]：取末段 basename，在所在目录查找 .md
    while IFS= read -r wl; do
      [ -z "$wl" ] && continue
      any_ref=true
      [[ "$wl" == http* ]] && continue
      local wl_base="${wl##*/}"
      if [ ! -e "$ref_dir/$wl_base.md" ] && [ ! -e "$ref_dir/$wl_base" ] && [ ! -e "$ref_dir/$wl" ] && [ ! -e "$ref_dir/${wl}.md" ]; then
        broken+=("$(basename "$ref_file") -> [[$wl]]")
      fi
    done < <(grep -oE '\[\[[^]]+\]\]' "$ref_file" 2>/dev/null | sed 's/\[\[//; s/\]\]//' | grep -v '^http' || true)

    # 2) markdown 路径引用 ](path)：相对该文件目录解析
    while IFS= read -r xref; do
      [ -z "$xref" ] && continue
      any_ref=true
      [[ "$xref" == http* ]] && continue
      [[ "$xref" == \#* ]] && continue
      [[ "$xref" == *"{"* ]] && continue
      if [ ! -e "$ref_dir/$xref" ]; then
        broken+=("$(basename "$ref_file") -> $xref")
      fi
    done < <(grep -oE '\]\([^)]+\)' "$ref_file" 2>/dev/null | sed 's/](\(.*\))/\1/' | grep -v '^http' | grep -v '^#' || true)
  done < <(find "$shared_dir" -type f -name "*.md" -print0 2>/dev/null)

  if [ ${#broken[@]} -eq 0 ]; then
    if [ "$any_ref" = true ]; then
      echo "  [PASS] no broken wikilinks/path refs in references/shared/"
    else
      echo "  [PASS] references/shared/ has no internal refs to validate"
    fi
    PASS=$((PASS + 1))
  else
    echo "  [FAIL] broken references in references/shared/:"
    for x in "${broken[@]}"; do
      echo "         -> $x"
    done
    errors=$((errors + 1))
    FAIL=$((FAIL + 1))
  fi
}

# ---------- Check 11/12/13: 引用审计（Python 脚本）----------
# 由 reference_audit.py 执行反向引用计数 + 循环引用检测 + Agent 调用方审计
run_reference_audit() {
  local audit_script="$PLUGIN_ROOT/scripts/reference_audit.py"
  if [ ! -f "$audit_script" ]; then
    echo ""
    echo "--- Check 11/12/13: reference audit ---"
    echo "  [SKIP] reference_audit.py not found"
    TOTAL=$((TOTAL + 3))
    PASS=$((PASS + 3))
    return
  fi

  local audit_output
  audit_output="$(python3 "$audit_script" 2>&1)" || true

  local in_check11=false in_check12=false in_check13=false
  local check11_result="PASS" check12_result="PASS" check13_result="PASS"

  echo ""
  while IFS= read -r line; do
    case "$line" in
      "--- Check 11:"*)
        in_check11=true; in_check12=false; in_check13=false
        TOTAL=$((TOTAL + 1))
        ;;
      "--- Check 12:"*)
        in_check11=false; in_check12=true; in_check13=false
        TOTAL=$((TOTAL + 1))
        ;;
      "--- Check 13:"*)
        in_check11=false; in_check12=false; in_check13=true
        TOTAL=$((TOTAL + 1))
        ;;
      CHECK11:PASS) check11_result="PASS"; PASS=$((PASS + 1)) ;;
      CHECK11:WARN) check11_result="WARN"; WARN=$((WARN + 1)) ;;
      CHECK12:PASS) check12_result="PASS"; PASS=$((PASS + 1)) ;;
      CHECK12:WARN) check12_result="WARN"; WARN=$((WARN + 1)) ;;
      CHECK12:FAIL) check12_result="FAIL"; FAIL=$((FAIL + 1)) ;;
      CHECK13:PASS) check13_result="PASS"; PASS=$((PASS + 1)) ;;
      CHECK13:WARN) check13_result="WARN"; WARN=$((WARN + 1)) ;;
      CHECK11_COUNT:*) ;;
      *)
        if [ "$in_check11" = true ] || [ "$in_check12" = true ] || [ "$in_check13" = true ]; then
          echo "$line"
        fi
        ;;
    esac
  done <<< "$audit_output"
}

# ---------- Check 14: 链路审计（audit-pipeline.py）----------
# 五类链路不变量：文件引用可解析 / 交叉引用指向存活 / 部署模板规范命令名 /
# 配置引用 hook 存在 / 清单计数与版本一致。脚本以退出码表达高优先级问题。
run_pipeline_audit() {
  local audit_script="$PLUGIN_ROOT/scripts/audit-pipeline.py"
  TOTAL=$((TOTAL + 1))
  echo ""
  echo "--- Check 14: pipeline audit (链路不变量) ---"
  if [ ! -f "$audit_script" ]; then
    echo "  [SKIP] audit-pipeline.py not found"
    PASS=$((PASS + 1))
    return
  fi

  local audit_output audit_rc=0
  audit_output="$(python3 "$audit_script" 2>&1)" || audit_rc=$?

  if [ "$audit_rc" -eq 0 ]; then
    # 透传 WARN 行（若有），但不阻断
    echo "$audit_output" | grep -E '⚠️|WARN' || true
    echo "  [PASS] all pipeline invariants hold"
    PASS=$((PASS + 1))
  else
    echo "$audit_output" | grep -E '❌|⚠️|:[0-9]+' || true
    echo "  [FAIL] pipeline audit reported high-priority issues"
    FAIL=$((FAIL + 1))
  fi
}

run_repo_hygiene() {
  local hygiene_script="$PLUGIN_ROOT/scripts/check-repo-hygiene.sh"
  TOTAL=$((TOTAL + 1))
  echo ""
  echo "--- Check 15: repo hygiene (依赖/构建/缓存产物不入库) ---"
  if [ ! -f "$hygiene_script" ]; then
    echo "  [SKIP] check-repo-hygiene.sh not found"
    PASS=$((PASS + 1))
    return
  fi

  local hygiene_output hygiene_rc=0
  hygiene_output="$(bash "$hygiene_script" 2>&1)" || hygiene_rc=$?

  if [ "$hygiene_rc" -eq 0 ]; then
    echo "  [PASS] repo hygiene clean — 无依赖/构建/缓存产物被跟踪"
    PASS=$((PASS + 1))
  else
    echo "$hygiene_output" | grep -E '\[FAIL\]|e\.g\.' || true
    echo "  [FAIL] repo hygiene 校验发现被跟踪的产物目录"
    FAIL=$((FAIL + 1))
  fi
}

# ---------- main ----------

echo "Skill Static Check (write-novel)"
echo "================================="
echo "Plugin: $PLUGIN_ROOT"

for skill_dir in "$SKILLS_DIR"/*/; do
  check_skill "$skill_dir"
done

# 跨 skill 顶层检查（在 per-skill 循环之后）
check_shared_references
run_reference_audit
run_pipeline_audit
run_repo_hygiene

echo ""
echo "================================="
echo "Total: $TOTAL | Pass: $PASS | Fail: $FAIL | Warn: $WARN"

if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
