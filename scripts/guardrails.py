import os
from typing import Dict, List

from scripts.encoding_utils import ensure_nfc


PROTECTED_DIRS = [".claude", "docs", "openspec"]
DERIVED_DIRS = [".write-novel", ".pytest_cache"]
DERIVED_FILES = ["当前Prompt.xml", "dashboard-data.json", "status-report.json"]
SOURCE_DIRS = ["人物", "世界设定", "分卷大纲", "章节草稿", "历史章节摘要", "全局设定"]
SOURCE_FILES = ["全局写作状态.md", "伏笔与线索回收池.md", "人物卡片模板.md", "分卷与单章细纲模板.md", "分卷大纲模板.md", "世界设定模板.md"]


def normalize_inside(project_root: str, target_path: str) -> str:
    root = ensure_nfc(os.path.realpath(os.path.abspath(project_root)))
    path = ensure_nfc(target_path if os.path.isabs(target_path) else os.path.join(root, target_path))
    path = os.path.realpath(os.path.abspath(path))
    if os.path.commonpath([root, path]) != root:
        raise ValueError(f"路径越界：{target_path}")
    return ensure_nfc(path)


def classify_path(project_root: str, target_path: str) -> Dict[str, str]:
    root = ensure_nfc(os.path.realpath(os.path.abspath(project_root)))
    path = normalize_inside(root, target_path)
    rel = ensure_nfc(os.path.relpath(path, root))
    first = rel.split(os.sep)[0]
    if rel in SOURCE_FILES or first in SOURCE_DIRS:
        kind = "source"
    elif rel in DERIVED_FILES or first in DERIVED_DIRS:
        kind = "derived"
    elif first in PROTECTED_DIRS:
        kind = "protected"
    else:
        kind = "project"
    return {"path": path, "relative_path": rel, "kind": kind}


def check_write_allowed(project_root: str, target_path: str, allow_protected: bool = False, allow_derived: bool = True) -> Dict[str, object]:
    try:
        info = classify_path(project_root, target_path)
    except ValueError as exc:
        return {
            "path": ensure_nfc(target_path),
            "relative_path": ensure_nfc(target_path),
            "kind": "outside",
            "allowed": False,
            "message": str(exc),
        }
    if info["kind"] == "protected" and not allow_protected:
        return {**info, "allowed": False, "message": "目标位于受保护目录"}
    if info["kind"] == "derived" and not allow_derived:
        return {**info, "allowed": False, "message": "目标是派生文件或缓存目录"}
    return {**info, "allowed": True, "message": "允许写入"}


def preflight_summary(project_root: str) -> Dict[str, object]:
    root = ensure_nfc(os.path.abspath(project_root))
    return {
        "project_root": root,
        "protected_dirs": PROTECTED_DIRS,
        "derived_dirs": DERIVED_DIRS,
        "source_files": SOURCE_FILES,
        "recommended_commands": [
            "python scripts/main.py doctor",
            "python scripts/main.py status",
            "python scripts/main.py assemble --chapter N --volume V",
            "python scripts/main.py continue --chapter-body-file FILE --chapter N --volume V",
        ],
    }


def format_preflight_text(summary: Dict[str, object]) -> str:
    lines = [
        "write-novel preflight",
        f"项目：{summary['project_root']}",
        f"受保护目录：{', '.join(summary['protected_dirs'])}",
        f"派生目录：{', '.join(summary['derived_dirs'])}",
        "推荐入口：",
    ]
    for command in summary["recommended_commands"]:
        lines.append(f"- {command}")
    return "\n".join(lines)
