import json
import os
from typing import Any, Dict, List

from scripts.encoding_utils import ensure_nfc
from scripts.workflow_contracts import load_current_task, validate_workflows, write_risk_list, write_status_report


SEVERITY_ORDER = {"ok": 0, "info": 1, "warning": 2, "error": 3}


def make_check(name: str, status: str, message: str, path: str = "", hint: str = "") -> Dict[str, str]:
    return {
        "name": name,
        "status": status,
        "path": path,
        "message": message,
        "hint": hint,
    }


def run_doctor(project_root: str) -> Dict[str, Any]:
    root = ensure_nfc(os.path.abspath(project_root))
    checks: List[Dict[str, str]] = []
    assets = required_asset_paths(root)

    for path in assets["files"]:
        exists = os.path.isfile(path)
        checks.append(make_check(
            "required_file",
            "ok" if exists else "error",
            "文件存在" if exists else "缺少必需文件",
            relpath(path, root),
            "运行 init 或从模板恢复该文件。" if not exists else "",
        ))

    for path in assets["dirs"]:
        exists = os.path.isdir(path)
        checks.append(make_check(
            "required_dir",
            "ok" if exists else "error",
            "目录存在" if exists else "缺少必需目录",
            relpath(path, root),
            "运行 init 或手动创建该目录。" if not exists else "",
        ))

    for issue in collect_frontmatter_issues(root):
        checks.append(make_check(
            "frontmatter",
            "warning",
            issue["message"],
            issue["file"],
            "补齐 YAML Frontmatter，或检查中文冒号/缩进。",
        ))

    for item in find_unresolved_wikilinks(root):
        checks.append(make_check(
            "wikilink",
            "error",
            item["message"],
            item["file"],
            "创建目标文件或修正 Wikilink。",
        ))

    for dep in dependency_status():
        checks.append(make_check(
            "dependency",
            dep["status"],
            dep["message"],
            dep["name"],
            "pip install -r scripts/requirements.txt" if dep["status"] == "error" else "",
        ))

    status = "ok"
    if any(check["status"] == "error" for check in checks):
        status = "error"
    elif any(check["status"] == "warning" for check in checks):
        status = "warning"

    return {
        "project_root": root,
        "status": status,
        "checks": checks,
        "summary": {
            "total": len(checks),
            "ok": sum(1 for check in checks if check["status"] == "ok"),
            "warning": sum(1 for check in checks if check["status"] == "warning"),
            "error": sum(1 for check in checks if check["status"] == "error"),
        },
    }


def build_status_report(project_root: str) -> Dict[str, Any]:
    inventory = project_inventory(project_root)
    risks = project_risks(project_root)
    next_action = "继续完善设定或运行 assemble 组装下一章 Prompt。"
    if any(risk["type"] == "unresolved_wikilink" for risk in risks):
        next_action = "先修复未解析 Wikilink，避免 Prompt 缺少关键上下文。"
    elif any(risk["type"] == "overdue_foreshadowing" for risk in risks):
        next_action = "优先安排逾期伏笔回收或调整回收计划。"
    elif not inventory.get("chapter_count"):
        next_action = "创建第一章细纲后运行 assemble。"

    return {
        "project_root": inventory["project_root"],
        "status": "error" if any(r["severity"] == "error" for r in risks) else "warning" if risks else "ok",
        "inventory": inventory,
        "risks": risks,
        "next_action": next_action,
    }


def format_doctor_text(result: Dict[str, Any]) -> str:
    lines = [
        "=" * 50,
        "  write-novel 项目健康诊断",
        "=" * 50,
        f"项目：{result['project_root']}",
        f"状态：{result['status']}",
        f"检查：{result['summary']['ok']} ok / {result['summary']['warning']} warning / {result['summary']['error']} error",
    ]
    for check in result["checks"]:
        if check["status"] == "ok":
            continue
        lines.append(f"[{check['status']}] {check['path']} — {check['message']}")
        if check.get("hint"):
            lines.append(f"  建议：{check['hint']}")
    lines.append("=" * 50)
    return "\n".join(lines)


def format_status_text(report: Dict[str, Any]) -> str:
    inv = report["inventory"]
    lines = [
        "=" * 50,
        "  write-novel 项目写作状态",
        "=" * 50,
        f"项目：{report['project_root']}",
        f"当前分卷：第{inv.get('current_volume', '?')}卷",
        f"当前章节：第{inv.get('current_chapter', '?')}章",
        f"进度：{inv.get('completed_chapters', 0)} 章 / {inv.get('completed_words', 0)} 字",
        f"章节文件：{inv.get('chapter_count', 0)} 个，摘要：{inv.get('summary_count', 0)} 个",
        f"主角：{inv.get('protagonist') or '?'}",
        f"最后更新：{inv.get('last_updated') or '?'}",
        f"伏笔：总数 {inv['foreshadowing']['total']} / 已回收 {inv['foreshadowing']['resolved']} / 发展中 {inv['foreshadowing']['developing']}",
    ]
    if report["risks"]:
        lines.append("风险：")
        for risk in report["risks"]:
            lines.append(f"- [{risk['severity']}] {risk['file']} — {risk['message']}")
    lines.append(f"下一步：{report['next_action']}")
    lines.append("=" * 50)
    return "\n".join(lines)


def dump_json(data: Dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, default=str)
