import os
import time
from typing import Any, Dict, List, Optional, Tuple

from scripts.encoding_utils import ensure_nfc, safe_open
from scripts.frontmatter_parser import parse_frontmatter, parse_frontmatter_string
from scripts.state_updater import _rebuild_markdown_with_frontmatter, backup_file


STAGES = [
    "project_setup",
    "outline_ready",
    "draft_done",
    "review_done",
    "deslop_done",
    "chapter_committed",
    "global_state_updated",
    "backup_done",
]

STAGE_LABELS = {
    "project_setup": "项目设置",
    "outline_ready": "细纲准备",
    "draft_done": "起草完成",
    "review_done": "审稿完成",
    "deslop_done": "去 AI 味完成",
    "chapter_committed": "章节提交",
    "global_state_updated": "全局状态更新",
    "backup_done": "备份完成",
}

STAGE_PREREQUISITES = {
    "project_setup": [],
    "outline_ready": ["project_setup"],
    "draft_done": ["project_setup", "outline_ready"],
    "review_done": ["project_setup", "outline_ready", "draft_done"],
    "deslop_done": ["project_setup", "outline_ready", "draft_done", "review_done"],
    "chapter_committed": ["project_setup", "outline_ready", "draft_done", "review_done", "deslop_done"],
    "global_state_updated": ["project_setup", "outline_ready", "draft_done", "review_done", "deslop_done", "chapter_committed"],
    "backup_done": ["project_setup", "outline_ready", "draft_done", "review_done", "deslop_done", "chapter_committed", "global_state_updated"],
}


def chapter_outline_path(project_root: str, volume_num: int, chapter_num: int) -> str:
    return ensure_nfc(os.path.join(project_root, "分卷大纲", f"第{volume_num}卷_细纲_第{chapter_num}章.md"))


def find_chapter_draft(project_root: str, chapter_num: int) -> Optional[str]:
    draft_dir = ensure_nfc(os.path.join(project_root, "章节草稿"))
    if not os.path.isdir(draft_dir):
        return None
    for name in sorted(os.listdir(draft_dir)):
        if name.startswith(f"第{chapter_num}章") and name.endswith(".md"):
            return ensure_nfc(os.path.join(draft_dir, name))
    return None


def infer_stage_state(project_root: str, volume_num: int, chapter_num: int) -> Dict[str, bool]:
    project_root = ensure_nfc(os.path.abspath(project_root))
    state = {stage: False for stage in STAGES}
    state["project_setup"] = os.path.isfile(os.path.join(project_root, "全局写作状态.md")) and os.path.isfile(os.path.join(project_root, "伏笔与线索回收池.md"))
    state["outline_ready"] = os.path.isfile(chapter_outline_path(project_root, volume_num, chapter_num))
    draft = find_chapter_draft(project_root, chapter_num)
    state["draft_done"] = draft is not None
    state["chapter_committed"] = draft is not None
    summary_path = os.path.join(project_root, "历史章节摘要", f"第{chapter_num}章_摘要.md")
    state["global_state_updated"] = os.path.isfile(summary_path)
    state["backup_done"] = any(os.path.isfile(path + ".bak") for path in [os.path.join(project_root, "全局写作状态.md"), chapter_outline_path(project_root, volume_num, chapter_num)])

    if draft:
        fm, _ = parse_frontmatter(draft)
        for stage in ["review_done", "deslop_done", "chapter_committed", "global_state_updated", "backup_done"]:
            if fm.get(stage) is True or fm.get(stage) == "true":
                state[stage] = True
        workflow = fm.get("写作阶段") or fm.get("writing_stage")
        if workflow in STAGES:
            state[workflow] = True
    return state


def next_stage(project_root: str, volume_num: int, chapter_num: int) -> Optional[str]:
    state = infer_stage_state(project_root, volume_num, chapter_num)
    for stage in STAGES:
        if not state[stage]:
            return stage
    return None


def check_stage_transition(project_root: str, volume_num: int, chapter_num: int, target_stage: str) -> Tuple[bool, List[str]]:
    if target_stage not in STAGES:
        return False, [f"未知阶段：{target_stage}"]
    state = infer_stage_state(project_root, volume_num, chapter_num)
    missing = [stage for stage in STAGE_PREREQUISITES[target_stage] if not state.get(stage)]
    return not missing, missing


def record_override(project_root: str, volume_num: int, chapter_num: int, target_stage: str, reason: str) -> str:
    project_root = ensure_nfc(os.path.abspath(project_root))
    state_path = ensure_nfc(os.path.join(project_root, "全局写作状态.md"))
    if not os.path.isfile(state_path):
        raise FileNotFoundError(state_path)
    backup_file(state_path)
    with safe_open(state_path, "r", encoding="utf-8") as f:
        original = f.read()
    fm, body = parse_frontmatter_string(original)
    overrides = fm.get("写作阶段Override", [])
    if not isinstance(overrides, list):
        overrides = [str(overrides)]
    overrides.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')} 第{volume_num}卷第{chapter_num}章 {target_stage}: {reason}")
    fm["写作阶段Override"] = overrides
    with safe_open(state_path, "w", encoding="utf-8") as f:
        f.write(_rebuild_markdown_with_frontmatter(fm, body))
    return state_path


def mark_stage(project_root: str, volume_num: int, chapter_num: int, stage: str, value: bool = True) -> str:
    if stage not in STAGES:
        raise ValueError(f"未知阶段：{stage}")
    draft = find_chapter_draft(project_root, chapter_num)
    if not draft:
        raise FileNotFoundError(f"未找到第{chapter_num}章草稿")
    backup_file(draft)
    with safe_open(draft, "r", encoding="utf-8") as f:
        original = f.read()
    fm, body = parse_frontmatter_string(original)
    fm[stage] = value
    if value:
        fm["写作阶段"] = stage
        fm["最后阶段更新时间"] = time.strftime("%Y-%m-%d %H:%M:%S")
    with safe_open(draft, "w", encoding="utf-8") as f:
        f.write(_rebuild_markdown_with_frontmatter(fm, body))
    return draft


def explain_state(project_root: str, volume_num: int, chapter_num: int) -> Dict[str, Any]:
    state = infer_stage_state(project_root, volume_num, chapter_num)
    upcoming = next_stage(project_root, volume_num, chapter_num)
    missing = []
    if upcoming:
        _, missing = check_stage_transition(project_root, volume_num, chapter_num, upcoming)
    return {
        "volume": volume_num,
        "chapter": chapter_num,
        "stages": [
            {"id": stage, "label": STAGE_LABELS[stage], "done": state[stage]}
            for stage in STAGES
        ],
        "next_stage": upcoming,
        "next_stage_label": STAGE_LABELS.get(upcoming, "全部完成") if upcoming else "全部完成",
        "missing_prerequisites": missing,
        "recommendation": _recommendation(upcoming, missing),
    }


def _recommendation(upcoming: Optional[str], missing: List[str]) -> str:
    if not upcoming:
        return "本章写作流程已完成。"
    if missing:
        labels = "、".join(STAGE_LABELS[item] for item in missing)
        return f"先完成前置阶段：{labels}。"
    actions = {
        "project_setup": "先运行 init 或补齐全局状态和伏笔池。",
        "outline_ready": "创建本章细纲。",
        "draft_done": "运行 assemble 后起草正文。",
        "review_done": "运行多视角审稿。",
        "deslop_done": "运行去 AI 味处理。",
        "chapter_committed": "执行 continue 或章节提交。",
        "global_state_updated": "更新全局状态、摘要与伏笔池。",
        "backup_done": "确认关键文件备份已生成。",
    }
    return actions[upcoming]


def format_state_text(state: Dict[str, Any]) -> str:
    lines = [f"第{state['volume']}卷第{state['chapter']}章写作状态："]
    for stage in state["stages"]:
        mark = "x" if stage["done"] else " "
        lines.append(f"- [{mark}] {stage['label']} ({stage['id']})")
    lines.append(f"下一阶段：{state['next_stage_label']}")
    lines.append(f"建议：{state['recommendation']}")
    return "\n".join(lines)
