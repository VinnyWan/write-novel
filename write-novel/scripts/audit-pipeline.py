#!/usr/bin/env python3
# write-novel 链路审计工具。
# 确定性校验 skill/agent 全链路：文件引用可解析、交叉引用指向存活目标、
# 部署模板使用规范命令名、配置引用的 hook 存在、清单计数/版本一致。
# 只做客观链路校验，不做创作判断。退出码：存在高优先级问题时非零。

import json
import os
import re
import sys

# 插件根 = 本脚本所在的 scripts/ 的上一级
PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 仓库根 = 插件根的上一级（marketplace.json 在仓库根）
REPO_ROOT = os.path.dirname(PLUGIN_ROOT)

# 废弃别名 skill → 规范名。合并历史见各别名 SKILL.md「已合并至」。
# 新增合并时在此处集中维护。
DEPRECATED_ALIASES = {
    "write-novel-long-analyze": "write-novel-analyze",
    "write-novel-short-analyze": "write-novel-analyze",
    "write-novel-long-scan": "write-novel-scan",
    "write-novel-short-scan": "write-novel-scan",
    "write-novel-plan": "write-novel-long-write",
}

# 引用路径提取：scripts/references/templates/hooks/assets/agents 下的带扩展名文件
REF_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_./-])"
    r"((?:scripts|references|templates|hooks|assets|agents)/[A-Za-z0-9_./-]+"
    r"\.(?:tmpl|py|md|sh|json|js|txt|csv|yaml|yml))"
)
ALIAS_RE = re.compile("|".join(re.escape(a) for a in DEPRECATED_ALIASES))

# 问题分类：是否高优先级（影响退出码）
SEVERITY = {
    "BROKEN_REF": "error",
    "STALE_CALLER": "error",
    "DEPLOY_STALE_CMD": "error",
    "HOOK_NAME_MISMATCH": "error",
    "MANIFEST_COUNT_MISMATCH": "error",
    "VERSION_MISMATCH": "error",
    "DOC_STALE_NAME": "warn",
}

findings = []


def add(category, path, line, message):
    rel = os.path.relpath(path, PLUGIN_ROOT)
    findings.append((category, rel, line, message))


def strip_frontmatter(text):
    # 返回 (frontmatter文本, 正文文本, 正文起始行号)
    if text.startswith("---"):
        parts = text.split("\n")
        end = None
        for i in range(1, len(parts)):
            if parts[i].strip() == "---":
                end = i
                break
        if end is not None:
            fm = "\n".join(parts[1:end])
            body = "\n".join(parts[end + 1:])
            return fm, body, end + 2
    return "", text, 1


def iter_targets():
    skills_dir = os.path.join(PLUGIN_ROOT, "skills")
    for name in sorted(os.listdir(skills_dir)):
        p = os.path.join(skills_dir, name, "SKILL.md")
        if os.path.isfile(p):
            yield p, os.path.join(skills_dir, name)
    agents_dir = os.path.join(PLUGIN_ROOT, "agents")
    for name in sorted(os.listdir(agents_dir)):
        if name.endswith(".md"):
            yield os.path.join(agents_dir, name), agents_dir


# --- 检查 1：文件引用可解析 ---
def check_broken_refs():
    for fpath, skillroot in iter_targets():
        text = open(fpath, encoding="utf-8").read()
        _, body, base_line = strip_frontmatter(text)
        fdir = os.path.dirname(fpath)
        for m in REF_PATH_RE.finditer(body):
            ref = m.group(1)
            line = base_line + body[: m.start()].count("\n")
            cands = [
                os.path.join(fdir, ref),
                os.path.join(skillroot, ref),
                os.path.join(PLUGIN_ROOT, ref),
            ]
            if not any(os.path.exists(c) for c in cands):
                add("BROKEN_REF", fpath, line, f"引用缺失：{ref}")


# --- 检查 2：交叉引用指向存活（agent 调用方元数据） ---
def check_stale_callers():
    agents_dir = os.path.join(PLUGIN_ROOT, "agents")
    for name in sorted(os.listdir(agents_dir)):
        if not name.endswith(".md"):
            continue
        fpath = os.path.join(agents_dir, name)
        text = open(fpath, encoding="utf-8").read()
        fm, _, _ = strip_frontmatter(text)
        for i, raw in enumerate(fm.split("\n"), start=2):
            if raw.lstrip().startswith("合并自"):
                continue
            for m in ALIAS_RE.finditer(raw):
                alias = m.group(0)
                add(
                    "STALE_CALLER",
                    fpath,
                    i,
                    f"调用方元数据使用废弃别名 {alias}，应为 {DEPRECATED_ALIASES[alias]}",
                )


# --- 检查 3：部署模板使用规范命令名 ---
def check_deploy_stale_cmd():
    tmpl_root = os.path.join(
        PLUGIN_ROOT, "skills", "write-novel-setup", "references", "templates"
    )
    if not os.path.isdir(tmpl_root):
        return
    for dirpath, _, files in os.walk(tmpl_root):
        for fn in files:
            if not (fn.endswith((".tmpl", ".sh", ".md", ".json"))):
                continue
            fpath = os.path.join(dirpath, fn)
            for i, raw in enumerate(open(fpath, encoding="utf-8"), start=1):
                if raw.lstrip().startswith("合并自"):
                    continue
                for m in ALIAS_RE.finditer(raw):
                    alias = m.group(0)
                    add(
                        "DEPLOY_STALE_CMD",
                        fpath,
                        i,
                        f"部署模板出现废弃命令 {alias}，应为 {DEPRECATED_ALIASES[alias]}",
                    )


# --- 检查 4：配置引用的 hook 文件存在 ---
def _hook_refs(json_path):
    if not os.path.isfile(json_path):
        return []
    txt = open(json_path, encoding="utf-8").read()
    return re.findall(r"/hooks/([A-Za-z0-9_.-]+\.(?:sh|py))", txt)


def check_hook_names():
    # 部署侧：settings-hooks.json → templates/hooks/
    tmpl = os.path.join(
        PLUGIN_ROOT, "skills", "write-novel-setup", "references", "templates"
    )
    settings = os.path.join(tmpl, "settings-hooks.json")
    hooks_dir = os.path.join(tmpl, "hooks")
    for hk in _hook_refs(settings):
        if not os.path.isfile(os.path.join(hooks_dir, hk)):
            add("HOOK_NAME_MISMATCH", settings, 1, f"settings 引用的部署 hook 缺失：{hk}")
    # 运行态：hooks/hooks.json → hooks/
    plugin_hooks_json = os.path.join(PLUGIN_ROOT, "hooks", "hooks.json")
    plugin_hooks_dir = os.path.join(PLUGIN_ROOT, "hooks")
    for hk in _hook_refs(plugin_hooks_json):
        if not os.path.isfile(os.path.join(plugin_hooks_dir, hk)):
            add(
                "HOOK_NAME_MISMATCH",
                plugin_hooks_json,
                1,
                f"hooks.json 引用的运行态 hook 缺失：{hk}",
            )


# --- 检查 5：清单计数与版本一致 ---
def _count_skills_agents():
    skills_dir = os.path.join(PLUGIN_ROOT, "skills")
    canonical, alias = 0, 0
    for name in sorted(os.listdir(skills_dir)):
        sp = os.path.join(skills_dir, name, "SKILL.md")
        if not os.path.isfile(sp):
            continue
        # 别名判定用确定性的废弃名集合，而非正文文案（路由器正文也含「已合并至」）
        if name in DEPRECATED_ALIASES:
            alias += 1
        else:
            canonical += 1
    agents_dir = os.path.join(PLUGIN_ROOT, "agents")
    agents = sum(1 for n in os.listdir(agents_dir) if n.endswith(".md"))
    return canonical, alias, agents


def check_manifest():
    canonical, alias, agents = _count_skills_agents()
    mk_path = os.path.join(REPO_ROOT, ".claude-plugin", "marketplace.json")
    pj_path = os.path.join(PLUGIN_ROOT, ".claude-plugin", "plugin.json")
    mk = json.load(open(mk_path, encoding="utf-8")) if os.path.isfile(mk_path) else {}
    pj = json.load(open(pj_path, encoding="utf-8")) if os.path.isfile(pj_path) else {}

    plugins = mk.get("plugins", [])
    entry = plugins[0] if plugins else {}
    desc = entry.get("description", "")
    sm = re.search(r"(\d+)\s*个?\s*Skills", desc)
    am = re.search(r"(\d+)\s*个?\s*Agents", desc)
    if sm and int(sm.group(1)) != canonical:
        add(
            "MANIFEST_COUNT_MISMATCH",
            mk_path,
            1,
            f"描述声明 {sm.group(1)} Skills，实测规范 skill {canonical} 个（另有 {alias} 个兼容别名）",
        )
    if am and int(am.group(1)) != agents:
        add(
            "MANIFEST_COUNT_MISMATCH",
            mk_path,
            1,
            f"描述声明 {am.group(1)} Agents，实测 {agents} 个",
        )
    mk_ver = entry.get("version")
    pj_ver = pj.get("version")
    if mk_ver and pj_ver and mk_ver != pj_ver:
        add(
            "VERSION_MISMATCH",
            mk_path,
            1,
            f"marketplace 版本 {mk_ver} ≠ plugin.json 版本 {pj_ver}",
        )


# --- 检查 6（WARN）：参考文档正文中的废弃名 ---
def check_doc_stale_names():
    skills_dir = os.path.join(PLUGIN_ROOT, "skills")
    for dirpath, _, files in os.walk(skills_dir):
        if os.sep + "references" not in dirpath:
            continue
        if os.sep + "templates" in dirpath:
            continue  # 部署模板归检查 3
        for fn in files:
            if not fn.endswith(".md"):
                continue
            fpath = os.path.join(dirpath, fn)
            for i, raw in enumerate(open(fpath, encoding="utf-8"), start=1):
                low = raw.lstrip()
                if low.startswith("合并自") or low.startswith("sync-source"):
                    continue
                if ALIAS_RE.search(raw):
                    add("DOC_STALE_NAME", fpath, i, "参考文档正文出现废弃 skill 名")


def main():
    check_broken_refs()
    check_stale_callers()
    check_deploy_stale_cmd()
    check_hook_names()
    check_manifest()
    check_doc_stale_names()

    by_cat = {}
    for cat, rel, line, msg in findings:
        by_cat.setdefault(cat, []).append((rel, line, msg))

    errors = 0
    print("=" * 60)
    print("write-novel 链路审计报告")
    print("=" * 60)
    order = [
        "BROKEN_REF",
        "STALE_CALLER",
        "DEPLOY_STALE_CMD",
        "HOOK_NAME_MISMATCH",
        "MANIFEST_COUNT_MISMATCH",
        "VERSION_MISMATCH",
        "DOC_STALE_NAME",
    ]
    for cat in order:
        items = by_cat.get(cat, [])
        if not items:
            continue
        sev = SEVERITY[cat]
        tag = "❌ ERROR" if sev == "error" else "⚠️  WARN"
        print(f"\n{tag}  [{cat}]  共 {len(items)} 条")
        for rel, line, msg in items:
            print(f"  {rel}:{line}  {msg}")
        if sev == "error":
            errors += len(items)

    print("\n" + "-" * 60)
    if errors:
        print(f"结果：FAIL — {errors} 条高优先级问题")
        warns = sum(len(by_cat.get(c, [])) for c in by_cat if SEVERITY[c] == "warn")
        if warns:
            print(f"另有 {warns} 条 WARN（不阻断）")
        return 1
    warns = sum(len(by_cat.get(c, [])) for c in by_cat if SEVERITY[c] == "warn")
    if warns:
        print(f"结果：PASS（高优先级问题 0）— 另有 {warns} 条 WARN")
    else:
        print("结果：PASS — 全部链路不变量通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
