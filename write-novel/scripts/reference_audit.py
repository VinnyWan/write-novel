#!/usr/bin/env python3
"""reference_audit.py — 引用完整性审计

三合一扫描：
  1. 反向引用计数：找出零入度文件（潜在僵尸）
  2. 循环引用检测：检测 .md 文件间的引用环
  3. Agent 调用方审计：找出零调用方的 agent 定义

被 static-check.sh Check 11/12/13 调用。
"""

import os, sys, re, json
from collections import defaultdict

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(PLUGIN_ROOT, "skills")
AGENTS_DIR = os.path.join(PLUGIN_ROOT, "agents")
REFERENCES_ROOT = os.path.join(PLUGIN_ROOT, "references")
SHARED_DIR = os.path.join(REFERENCES_ROOT, "shared")
RULES_DIR = os.path.join(REFERENCES_ROOT, "rules")
METHODOLOGY_DIR = os.path.join(REFERENCES_ROOT, "methodology")

# ---- whitelist: files not expected to be referenced by .md ----
ZERO_REF_WHITELIST = {
    ".gitkeep", "MANIFEST.yaml", "README.md",
    "project-memory-init.json", "author_error_catalog.json",
    "author_glossary.json", "writing_references.json",
    # SKILL.md files are entry points, system-routed, not referenced by path
    "SKILL.md",
    # contract-schema is referenced only by evals
    "contract-schema.md",
    # UPGRADING.md has no .md references
    "UPGRADING.md",
}

# Directories whose files are deployment templates or runtime-loaded (hooks), not .md referenced
ZERO_REF_SKIP_DIRS = {
    "references/rules",
    "references/methodology",
    "references/archive",
}

# Subdirectories of skills that contain deployment templates, not .md references
ZERO_REF_SKIP_PREFIXES = (
    "skills/write-novel-setup/references/agent-references/",
    "skills/write-novel-setup/references/templates/",
)

# ---- file collection ----
def collect_files(exts=(".md",)):
    """Return list of (abs_path, rel_path) for all plugin files."""
    files = []
    for root, dirs, fnames in os.walk(SKILLS_DIR):
        # skip methodology and archive inside skills if they exist
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
        for fn in fnames:
            if fn.endswith(exts):
                abs_path = os.path.join(root, fn)
                rel_path = os.path.relpath(abs_path, PLUGIN_ROOT)
                files.append((abs_path, rel_path))
    for top_dir in (AGENTS_DIR, SHARED_DIR, RULES_DIR):
        if not os.path.isdir(top_dir):
            continue
        for root, dirs, fnames in os.walk(top_dir):
            dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
            for fn in fnames:
                if fn.endswith(exts):
                    abs_path = os.path.join(root, fn)
                    rel_path = os.path.relpath(abs_path, PLUGIN_ROOT)
                    files.append((abs_path, rel_path))
    return files


def build_basename_index(files):
    """Index: basename → list of rel_paths."""
    idx = defaultdict(list)
    for abs_path, rel_path in files:
        bn = os.path.basename(rel_path)
        idx[bn].append(rel_path)
    return idx


# ---- reference extraction ----
MD_LINK_RE = re.compile(r'\]\(([^)]+)\)')
WIKILINK_RE = re.compile(r'\[\[([^]]+)\]\]')
BACKTICK_RE = re.compile(r'`([^`]+\.md)`')
AGENT_REF_RE = re.compile(r'subagent_type\s*[:=]\s*"([^"]+)"')
AGENT_REF_UNQUOTED_RE = re.compile(r'subagent_type\s*[:=]\s*([a-z][a-z0-9_-]+)')

RUNTIME_DIRS = {"追踪", "设定", "大纲", "正文", "对标", "拆文库", "参考资料", ".story-system"}


def extract_references(abs_path, text):
    """Extract all internal file references from text. Returns list of ref strings."""
    refs = []

    # 1) Markdown links
    for m in MD_LINK_RE.finditer(text):
        link = m.group(1).strip()
        if link.startswith("http") or link.startswith("#"):
            continue
        refs.append(("link", link))

    # 2) Wikilinks
    for m in WIKILINK_RE.finditer(text):
        wl = m.group(1).strip()
        if wl.startswith("http"):
            continue
        refs.append(("wiki", wl))

    # 3) Backtick-wrapped .md paths
    for m in BACKTICK_RE.finditer(text):
        bt = m.group(1).strip()
        if any(bt.startswith(d + "/") for d in RUNTIME_DIRS):
            continue
        if not re.match(r'^[a-z0-9_/.-]+\.md$', bt):
            continue
        refs.append(("backtick", bt))

    # 4) Agent refs (from SKILL.md in skills/)
    if "/SKILL.md" in abs_path or abs_path.endswith("/SKILL.md"):
        for m in AGENT_REF_RE.finditer(text):
            agent_name = m.group(1)
            short = agent_name.replace("write-novel:", "")
            refs.append(("agent", f"agents/{short}.md"))
        for m in AGENT_REF_UNQUOTED_RE.finditer(text):
            agent_name = m.group(1)
            # Skip false matches that are not actually agent names
            if not agent_name.startswith("write-novel-"):
                continue
            short = agent_name.replace("write-novel:", "")
            refs.append(("agent", f"agents/{short}.md"))

    return refs


# ---- path resolution ----
def resolve_ref(ref_str, src_dir, basename_index):
    """Resolve a reference string to a canonical rel_path (or None)."""
    ref_base = os.path.basename(ref_str)

    # 1) Relative to source file directory
    candidate = os.path.normpath(os.path.join(src_dir, ref_str))
    if os.path.exists(os.path.join(PLUGIN_ROOT, candidate)):
        # Normalize away any ../
        return os.path.relpath(os.path.join(PLUGIN_ROOT, candidate), PLUGIN_ROOT)

    # 2) Relative to plugin root
    if os.path.exists(os.path.join(PLUGIN_ROOT, ref_str)):
        return ref_str

    # 3) By basename
    if ref_base in basename_index:
        candidates = basename_index[ref_base]
        # Prefer same skill or shared
        for c in candidates:
            if src_dir.startswith("skills/") and c.startswith(src_dir[:src_dir.index("/", 7)] if "/" in src_dir[7:] else src_dir):
                return c
        return candidates[0]

    # 4) Wikilink without .md extension
    if not ref_str.endswith(".md"):
        md_ref = ref_str + ".md"
        return resolve_ref(md_ref, src_dir, basename_index)

    return None


# ---- Check 11: reverse reference count ----
def check_reverse_references(files, basename_index):
    """Return (pass_bool, warn_bool, zero_ref_list)."""
    all_files = collect_files((".md",))
    all_files_dict = {rel: abs for abs, rel in all_files}

    src_files = [(abs, rel) for abs, rel in files
                 if rel.endswith(".md") and ("/SKILL.md" in rel or "/references/" in rel
                     or rel.startswith("agents/") or rel.startswith("references/shared/")
                     or rel.startswith("references/rules/"))]

    # Also add agents, shared, rules .md files as source files for reference extraction
    for abs, rel in all_files:
        if rel.startswith("agents/") or rel.startswith("references/shared/") or rel.startswith("references/rules/"):
            if (abs, rel) not in src_files:
                src_files.append((abs, rel))

    ref_count = defaultdict(int)

    for abs_path, rel_path in src_files:
        try:
            with open(abs_path, "r") as f:
                text = f.read()
        except Exception:
            continue

        src_dir = os.path.dirname(rel_path)
        refs = extract_references(abs_path, text)

        for ref_type, ref_str in refs:
            resolved = resolve_ref(ref_str, src_dir, basename_index)
            if resolved:
                ref_count[resolved] += 1

    # Find zero-reference .md files
    zero_refs = []
    for abs_path, rel_path in all_files:
        if not rel_path.endswith(".md"):
            continue
        bn = os.path.basename(rel_path)
        if bn in ZERO_REF_WHITELIST:
            continue
        # Skip files in deployment-template / runtime-loaded directories
        skip = False
        for skip_dir in ZERO_REF_SKIP_DIRS:
            if rel_path.startswith(skip_dir + "/") or rel_path == skip_dir:
                skip = True
                break
        if skip:
            continue
        for prefix in ZERO_REF_SKIP_PREFIXES:
            if rel_path.startswith(prefix):
                skip = True
                break
        if skip:
            continue
        # Skip .json and .yaml
        if bn.endswith(".json") or bn.endswith(".yaml"):
            continue
        if ref_count.get(rel_path, 0) == 0:
            zero_refs.append(rel_path)

    zero_refs.sort()
    return len(zero_refs) == 0, len(zero_refs) > 0, zero_refs


# ---- Check 12: cycle detection ----
def check_cyclic_references(files, basename_index):
    """Return (pass_bool, fail_bool, self_refs, cycles)."""
    # Only include references/ and shared/ files, exclude methodology
    nodes = set()
    for abs_path, rel_path in files:
        if "/references/" in rel_path and rel_path.endswith(".md"):
            nodes.add(rel_path)
        elif rel_path.startswith("references/shared/") and rel_path.endswith(".md"):
            nodes.add(rel_path)

    # Build adjacency
    adj = defaultdict(set)
    for abs_path, rel_path in files:
        if rel_path not in nodes:
            # But we still extract refs FROM nodes
            pass
        if not rel_path.endswith(".md"):
            continue

        try:
            with open(abs_path, "r") as f:
                text = f.read()
        except Exception:
            continue

        src_dir = os.path.dirname(rel_path)
        refs = extract_references(abs_path, text)

        for ref_type, ref_str in refs:
            resolved = resolve_ref(ref_str, src_dir, basename_index)
            if resolved and resolved in nodes:
                adj[rel_path].add(resolved)

    # DFS cycle detection
    self_refs = set()
    cycles = []

    visited = set()
    in_stack = set()

    for node in sorted(nodes):
        if node in visited:
            continue
        # Iterative DFS
        stack = [(node, iter(sorted(adj.get(node, set()))))]
        in_stack.add(node)

        while stack:
            cur, neighbors = stack[-1]
            try:
                nb = next(neighbors)
                if nb == cur:
                    self_refs.add(cur)
                    continue
                if nb in in_stack:
                    cycles.append((cur, nb))
                    continue
                if nb not in visited:
                    visited.add(nb)
                    in_stack.add(nb)
                    stack.append((nb, iter(sorted(adj.get(nb, set())))))
            except StopIteration:
                in_stack.discard(cur)
                visited.add(cur)
                stack.pop()

    self_refs = sorted(self_refs)
    cycles = sorted(set(cycles))
    has_cycle = len(cycles) > 0
    has_self = len(self_refs) > 0

    return not has_cycle, has_cycle, self_refs, cycles


# ---- Check 13: agent caller audit ----
def check_agent_callers():
    """Return (pass_bool, warn_bool, zero_caller_agents, non_conforming_files)."""
    if not os.path.isdir(AGENTS_DIR):
        return True, False, [], []

    # Agent definitions
    agent_defs = []
    for fn in os.listdir(AGENTS_DIR):
        if fn.endswith(".md"):
            agent_defs.append(fn[:-3])  # without .md

    # Non-conforming
    non_conforming = [fn + ".md" for fn in agent_defs
                      if not fn.startswith("write-novel-")]

    # Scan all SKILL.md AND references/*.md for subagent_type refs
    called = set()
    for root, dirs, fnames in os.walk(SKILLS_DIR):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
        for fn in fnames:
            if fn == "SKILL.md" or (fn.endswith(".md") and "/references/" in root.replace("\\", "/")):
                abs_path = os.path.join(root, fn)
                try:
                    with open(abs_path, "r") as f:
                        text = f.read()
                except Exception:
                    continue
                for m in AGENT_REF_RE.finditer(text):
                    agent_name = m.group(1).replace("write-novel:", "")
                    called.add(agent_name)
                for m in AGENT_REF_UNQUOTED_RE.finditer(text):
                    agent_name = m.group(1)
                    if agent_name.startswith("write-novel-"):
                        called.add(agent_name)

    zero_callers = sorted(set(agent_defs) - called)
    return len(zero_callers) == 0, len(zero_callers) > 0, zero_callers, non_conforming


# ---- main ----
def main():
    files = collect_files((".md",))
    basename_index = build_basename_index(files)

    # ---- Check 11 ----
    print("--- Check 11: reverse reference count ---")
    passed, warned, zero_refs = check_reverse_references(files, basename_index)
    if passed:
        print("  [PASS] no files with zero inbound references")
        print("CHECK11:PASS")
    else:
        print(f"  [WARN] files with zero inbound references (potential zombies): {len(zero_refs)}")
        # Group by directory
        prev_dir = ""
        for zr in zero_refs:
            d = os.path.dirname(zr)
            if d != prev_dir:
                print(f"         [{d}/]")
                prev_dir = d
            print(f"           {os.path.basename(zr)}")
        print("CHECK11:WARN")
        print(f"CHECK11_COUNT:{len(zero_refs)}")

    # ---- Check 12 ----
    print("--- Check 12: cyclic reference detection ---")
    passed_cyc, failed_cyc, self_refs, cycles = check_cyclic_references(files, basename_index)
    if self_refs:
        print(f"  [WARN] self-referencing files: {len(self_refs)}")
        for sr in self_refs:
            print(f"         → {sr}")
    if passed_cyc and not self_refs:
        print("  [PASS] no cyclic references detected")
    if failed_cyc:
        print(f"  [FAIL] cyclic references detected: {len(cycles)}")
        for src, tgt in cycles:
            print(f"         {src} → {tgt}")

    if failed_cyc:
        print("CHECK12:FAIL")
    elif self_refs:
        print("CHECK12:WARN")
    else:
        print("CHECK12:PASS")

    # ---- Check 13 ----
    print("--- Check 13: agent caller audit ---")
    passed_agt, warned_agt, zero_callers, non_conforming = check_agent_callers()
    if non_conforming:
        print(f"  [WARN] non-conforming files in agents/ (not write-novel-* pattern):")
        for nc in non_conforming:
            print(f"         → {nc}")
    if passed_agt and not non_conforming:
        print("  [PASS] all agent definitions have at least one caller")
    if warned_agt:
        print(f"  [WARN] agent definitions with zero skill callers:")
        for zc in zero_callers:
            print(f"         → {zc}")

    if warned_agt or non_conforming:
        print("CHECK13:WARN")
    else:
        print("CHECK13:PASS")


if __name__ == "__main__":
    main()
