import html
import json
import os
from typing import Any, Dict

from scripts.diagnostics import build_status_report, run_doctor
from scripts.encoding_utils import ensure_nfc, safe_open
from scripts.guardrails import check_write_allowed
from scripts.project_assets import project_inventory


DASHBOARD_DIR = ".write-novel"
DASHBOARD_DATA_FILE = "dashboard-data.json"
DASHBOARD_HTML_FILE = "dashboard.html"


def build_dashboard_data(project_root: str) -> Dict[str, Any]:
    inventory = project_inventory(project_root)
    status = build_status_report(project_root)
    doctor = run_doctor(project_root)
    return {
        "project": {
            "root": inventory["project_root"],
            "current_volume": inventory.get("current_volume"),
            "current_chapter": inventory.get("current_chapter"),
            "protagonist": inventory.get("protagonist"),
        },
        "progress": {
            "completed_chapters": inventory.get("completed_chapters", 0),
            "completed_words": inventory.get("completed_words", 0),
            "chapter_files": inventory.get("chapter_count", 0),
            "summaries": inventory.get("summary_count", 0),
        },
        "foreshadowing": inventory.get("foreshadowing", {}),
        "diagnostics": doctor["summary"],
        "risks": status["risks"],
        "next_action": status["next_action"],
    }


def write_dashboard_data(project_root: str) -> str:
    project_root = ensure_nfc(os.path.abspath(project_root))
    out_dir = ensure_nfc(os.path.join(project_root, DASHBOARD_DIR))
    check = check_write_allowed(project_root, out_dir, allow_derived=True)
    if not check["allowed"]:
        raise PermissionError(check["message"])
    os.makedirs(out_dir, exist_ok=True)
    out_path = ensure_nfc(os.path.join(out_dir, DASHBOARD_DATA_FILE))
    data = build_dashboard_data(project_root)
    with safe_open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return out_path


def write_dashboard_html(project_root: str) -> str:
    project_root = ensure_nfc(os.path.abspath(project_root))
    data = build_dashboard_data(project_root)
    out_dir = ensure_nfc(os.path.join(project_root, DASHBOARD_DIR))
    check = check_write_allowed(project_root, out_dir, allow_derived=True)
    if not check["allowed"]:
        raise PermissionError(check["message"])
    os.makedirs(out_dir, exist_ok=True)
    out_path = ensure_nfc(os.path.join(out_dir, DASHBOARD_HTML_FILE))
    html_text = render_dashboard_html(data)
    with safe_open(out_path, "w", encoding="utf-8") as f:
        f.write(html_text)
    write_dashboard_data(project_root)
    return out_path


def render_dashboard_html(data: Dict[str, Any]) -> str:
    def h(value: Any) -> str:
        return html.escape(str(value if value is not None else "?"))

    project = data.get("project", {})
    progress = data.get("progress", {})
    foreshadowing = data.get("foreshadowing", {})
    risks = data.get("risks", [])
    risk_items = "".join(
        f"<li><strong>{h(risk.get('severity', ''))}</strong> {h(risk.get('file', ''))}: {h(risk.get('message', ''))}</li>"
        for risk in risks
    ) or "<li>暂无风险</li>"
    return f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\">
  <title>write-novel dashboard</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 32px; line-height: 1.6; color: #1f2933; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; }}
    .card {{ border: 1px solid #d9e2ec; border-radius: 12px; padding: 16px; background: #fff; }}
    .metric {{ font-size: 28px; font-weight: 700; }}
    .muted {{ color: #60758a; }}
  </style>
</head>
<body>
  <h1>write-novel 写作状态面板</h1>
  <p class=\"muted\">只读派生视图，不修改源 Markdown 文件。</p>
  <div class=\"grid\">
    <section class=\"card\"><h2>项目</h2><p>主角：{h(project.get('protagonist'))}</p><p>当前：第{h(project.get('current_volume'))}卷 / 第{h(project.get('current_chapter'))}章</p></section>
    <section class=\"card\"><h2>进度</h2><div class=\"metric\">{h(progress.get('completed_chapters', 0))} 章</div><p>{h(progress.get('completed_words', 0))} 字</p></section>
    <section class=\"card\"><h2>伏笔</h2><p>总数：{h(foreshadowing.get('total', 0))}</p><p>已回收：{h(foreshadowing.get('resolved', 0))} / 发展中：{h(foreshadowing.get('developing', 0))}</p></section>
    <section class=\"card\"><h2>诊断</h2><p>OK：{h(data['diagnostics'].get('ok', 0))}</p><p>Warning：{h(data['diagnostics'].get('warning', 0))} / Error：{h(data['diagnostics'].get('error', 0))}</p></section>
  </div>
  <section class=\"card\"><h2>风险</h2><ul>{risk_items}</ul></section>
  <section class=\"card\"><h2>下一步</h2><p>{h(data.get('next_action', ''))}</p></section>
</body>
</html>
"""
