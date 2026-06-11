import glob
import os
import re
import time
from typing import Any, Dict, List, Optional

from scripts.encoding_utils import ensure_nfc, safe_open
from scripts.frontmatter_parser import parse_frontmatter, parse_frontmatter_string


WORKFLOW_DIR = "工作流"
REQUIRED_WORKFLOW_SECTIONS = {
    "总览.md": ["流程入口", "约定"],
    "日更续写.md": ["目的", "阶段表", "失败恢复", "相关文件"],
    "审稿去味.md": ["目的", "阶段表", "质量门禁", "相关文件"],
    "章节提交.md": ["目的", "阶段表", "Override 审计", "相关文件"],
    "当前任务.md": ["当前状态", "Override 审计"],
    "风险清单.md": ["说明"],
    "脚本治理.md": ["目的", "脚本清单", "新增脚本决策门禁"],
}


def workflow_path(project_root: str, name: str) -> str:
    return ensure_nfc(os.path.join(project_root, WORKFLOW_DIR, name))


def load_workflow(project_root: str, name: str) -> Dict[str, Any]:
    path = workflow_path(project_root, name)
    fm, body = parse_frontmatter(path)
    return {"path": path, "frontmatter": fm, "body": body, "sections": extract_sections(body)}


def extract_sections(body: str) -> Dict[str, str]:
    sections: Dict[str, str] = {}
    pattern = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
    matches = list(pattern.finditer(body))
    for index, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        sections[title] = body[start:end].strip()
    return sections


def parse_markdown_table(section_text: str) -> List[Dict[str, str]]:
    rows = [line.strip() for line in section_text.splitlines() if line.strip().startswith("|")]
    if len(rows) < 2:
        return []
    headers = [cell.strip() for cell in rows[0].strip("|").split("|")]
    data_rows = []
    for row in rows[2:]:
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        if len(cells) != len(headers):
            continue
        data_rows.append(dict(zip(headers, cells)))
    return data_rows


def load_stage_table(project_root: str, workflow_name: str = "日更续写.md") -> List[Dict[str, str]]:
    workflow = load_workflow(project_root, workflow_name)
    return parse_markdown_table(workflow["sections"].get("阶段表", ""))


def validate_workflows(project_root: str) -> List[Dict[str, str]]:
    issues: List[Dict[str, str]] = []
    for filename, sections in REQUIRED_WORKFLOW_SECTIONS.items():
        path = workflow_path(project_root, filename)
        rel = os.path.join(WORKFLOW_DIR, filename)
        if not os.path.isfile(path):
            issues.append({"file": rel, "message": "缺少工作流文件", "hint": "从项目模板恢复该 Markdown 工作流文件。"})
            continue
        try:
            workflow = load_workflow(project_root, filename)
        except (OSError, UnicodeDecodeError) as exc:
            issues.append({"file": rel, "message": f"读取失败：{exc}", "hint": "检查文件编码和权限。"})
            continue
        if not workflow["frontmatter"]:
            issues.append({"file": rel, "message": "缺少可解析 Frontmatter", "hint": "补齐流程ID/类型/版本等字段。"})
        for section in sections:
            if section not in workflow["sections"]:
                issues.append({"file": rel, "message": f"缺少章节：{section}", "hint": f"添加 `## {section}`。"})
        if "阶段表" in sections and not parse_markdown_table(workflow["sections"].get("阶段表", "")):
            issues.append({"file": rel, "message": "阶段表为空或格式不正确", "hint": "使用 Markdown 表格定义阶段。"})
    return issues


def load_current_task(project_root: str) -> Dict[str, Any]:
    path = workflow_path(project_root, "当前任务.md")
    if not os.path.isfile(path):
        return {}
    fm, body = parse_frontmatter(path)
    sections = extract_sections(body)
    status_rows = parse_markdown_table(sections.get("当前状态", ""))
    status = {row.get("字段", ""): row.get("值", "") for row in status_rows}
    return {"path": path, "frontmatter": fm, "status": status, "sections": sections}


def append_override_audit(project_root: str, volume_num: int, chapter_num: int, target_stage: str, missing: List[str], reason: str) -> str:
    path = workflow_path(project_root, "当前任务.md")
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    with safe_open(path, "r", encoding="utf-8") as f:
        content = f.read()
    row = f"| {time.strftime('%Y-%m-%d %H:%M:%S')} | {volume_num} | {chapter_num} | {target_stage} | {', '.join(missing)} | {reason} |"
    lines = content.splitlines()
    insert_at: Optional[int] = None
    for index, line in enumerate(lines):
        if line.startswith("|---") and index > 0 and "目标阶段" in lines[index - 1]:
            insert_at = index + 1
            break
    if insert_at is None:
        lines.append("\n## Override 审计")
        lines.append("\n| 时间 | 卷 | 章 | 目标阶段 | 跳过前置 | 原因 |")
        lines.append("|---|---|---|---|---|---|")
        lines.append(row)
    else:
        lines.insert(insert_at, row)
    with safe_open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return path


def write_risk_list(project_root: str, risks: List[Dict[str, Any]]) -> str:
    path = workflow_path(project_root, "风险清单.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = [
        "---",
        "类型: 风险清单",
        "版本: 1.0",
        f"最后更新时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "---",
        "",
        "# 风险清单",
        "",
        "| 严重级别 | 类型 | 文件 | 问题 | 恢复建议 |",
        "|---|---|---|---|---|",
    ]
    for risk in risks:
        lines.append(
            f"| {risk.get('severity', '')} | {risk.get('type', '')} | {risk.get('file', '')} | {risk.get('message', '')} | {risk.get('hint', '')} |"
        )
    lines.extend(["", "## 说明", "", "本文件由 doctor/report 可选更新，也允许作者手动补充。"])
    with safe_open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return path


def write_status_report(project_root: str, report: Dict[str, Any]) -> str:
    path = workflow_path(project_root, "状态报告.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    inventory = report.get("inventory", {})
    lines = [
        "---",
        "类型: 状态报告",
        "版本: 1.0",
        f"最后更新时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "---",
        "",
        "# 状态报告",
        "",
        "## 项目进度",
        "",
        "| 字段 | 值 |",
        "|---|---|",
        f"| 当前分卷 | {inventory.get('current_volume', '')} |",
        f"| 当前章节 | {inventory.get('current_chapter', '')} |",
        f"| 已完成章数 | {inventory.get('completed_chapters', 0)} |",
        f"| 已完成字数 | {inventory.get('completed_words', 0)} |",
        f"| 主角 | {inventory.get('protagonist') or ''} |",
        "",
        "## 风险摘要",
        "",
        "| 严重级别 | 类型 | 文件 | 问题 |",
        "|---|---|---|---|",
    ]
    for risk in report.get("risks", []):
        lines.append(f"| {risk.get('severity', '')} | {risk.get('type', '')} | {risk.get('file', '')} | {risk.get('message', '')} |")
    lines.extend(["", "## 下一步", "", str(report.get("next_action", ""))])
    with safe_open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return path
