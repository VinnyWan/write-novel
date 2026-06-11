import glob
import importlib.util
import os
from typing import Any, Dict, List, Optional

from scripts.encoding_utils import ensure_nfc
from scripts.foreshadowing_tracker import get_foreshadowing_stats, get_overdue_foreshadowing
from scripts.frontmatter_parser import parse_frontmatter
from scripts.wikilink_resolver import extract_wikilinks, resolve_wikilink_target


REQUIRED_FILES = [
    "全局写作状态.md",
    "伏笔与线索回收池.md",
    "人物卡片模板.md",
    "分卷与单章细纲模板.md",
    "分卷大纲模板.md",
    "世界设定模板.md",
]

REQUIRED_DIRS = [
    "全局设定",
    "分卷大纲",
    "章节草稿",
    "人物",
    "世界设定",
    "历史章节摘要",
]

IGNORED_SCAN_DIRS = {
    ".git",
    ".claude",
    ".pytest_cache",
    ".write-novel",
    "docs",
    "openspec",
}

SOURCE_MARKDOWN_PATTERNS = [
    "全局写作状态.md",
    "伏笔与线索回收池.md",
    "世界设定/**/*.md",
    "人物/**/*.md",
    "分卷大纲/**/*.md",
    "章节草稿/**/*.md",
    "历史章节摘要/**/*.md",
]


def normalize_project_root(project_root: Optional[str] = None) -> str:
    return ensure_nfc(os.path.abspath(project_root or os.getcwd()))


def relpath(path: str, project_root: str) -> str:
    return ensure_nfc(os.path.relpath(path, project_root))


def required_asset_paths(project_root: str) -> Dict[str, List[str]]:
    root = normalize_project_root(project_root)
    return {
        "files": [os.path.join(root, name) for name in REQUIRED_FILES],
        "dirs": [os.path.join(root, name) for name in REQUIRED_DIRS],
    }


def list_markdown_sources(project_root: str) -> List[str]:
    root = normalize_project_root(project_root)
    paths = []
    for pattern in SOURCE_MARKDOWN_PATTERNS:
        paths.extend(glob.glob(os.path.join(root, pattern), recursive=True))
    unique = []
    seen = set()
    for path in paths:
        path = ensure_nfc(path)
        if path in seen or not os.path.isfile(path):
            continue
        parts = set(os.path.relpath(path, root).split(os.sep))
        if parts & IGNORED_SCAN_DIRS:
            continue
        seen.add(path)
        unique.append(path)
    return sorted(unique)


def find_chapter_files(project_root: str) -> List[str]:
    draft_dir = os.path.join(normalize_project_root(project_root), "章节草稿")
    if not os.path.isdir(draft_dir):
        return []
    return sorted(
        ensure_nfc(os.path.join(draft_dir, name))
        for name in os.listdir(draft_dir)
        if name.endswith(".md") and os.path.isfile(os.path.join(draft_dir, name))
    )


def find_unresolved_wikilinks(project_root: str) -> List[Dict[str, str]]:
    root = normalize_project_root(project_root)
    unresolved = []
    for path in list_markdown_sources(root):
        try:
            _, body = parse_frontmatter(path)
        except OSError as exc:
            unresolved.append({
                "file": relpath(path, root),
                "target": "",
                "message": f"读取失败：{exc}",
            })
            continue
        for target in extract_wikilinks(body):
            if resolve_wikilink_target(target, root) is None:
                unresolved.append({
                    "file": relpath(path, root),
                    "target": target,
                    "message": f"未解析的 Wikilink：[[{target}]]",
                })
    return unresolved


def collect_frontmatter_issues(project_root: str) -> List[Dict[str, str]]:
    root = normalize_project_root(project_root)
    issues = []
    important_prefixes = ("人物/", "世界设定/", "分卷大纲/", "历史章节摘要/")
    important_files = {"全局写作状态.md", "伏笔与线索回收池.md"}
    for path in list_markdown_sources(root):
        rel = relpath(path, root)
        try:
            fm, _ = parse_frontmatter(path)
        except OSError as exc:
            issues.append({"file": rel, "message": f"读取失败：{exc}"})
            continue
        if rel in important_files or rel.startswith(important_prefixes):
            if not fm:
                issues.append({"file": rel, "message": "缺少可解析 Frontmatter"})
    return issues


def dependency_status() -> List[Dict[str, str]]:
    checks = []
    for module in ["yaml"]:
        present = importlib.util.find_spec(module) is not None
        checks.append({
            "name": module,
            "status": "ok" if present else "error",
            "message": "已安装" if present else "未安装，请运行 pip install -r scripts/requirements.txt",
        })
    return checks


def parse_chapter_number(value: Any, default: int = 1) -> int:
    if isinstance(value, int):
        return value
    text = str(value or '').strip()
    if text.isdigit():
        return int(text)
    return default


def project_inventory(project_root: str) -> Dict[str, Any]:
    root = normalize_project_root(project_root)
    assets = required_asset_paths(root)
    state_fm: Dict[str, Any] = {}
    state_path = os.path.join(root, "全局写作状态.md")
    if os.path.isfile(state_path):
        state_fm, _ = parse_frontmatter(state_path)
    chapters = find_chapter_files(root)
    summaries = glob.glob(os.path.join(root, "历史章节摘要", "*.md"))
    return {
        "project_root": root,
        "required_files": [relpath(path, root) for path in assets["files"]],
        "required_dirs": [relpath(path, root) for path in assets["dirs"]],
        "existing_required_files": [relpath(path, root) for path in assets["files"] if os.path.isfile(path)],
        "existing_required_dirs": [relpath(path, root) for path in assets["dirs"] if os.path.isdir(path)],
        "source_markdown_count": len(list_markdown_sources(root)),
        "chapter_count": len(chapters),
        "summary_count": len(summaries),
        "current_volume": state_fm.get("当前分卷"),
        "current_chapter": state_fm.get("当前章节"),
        "completed_chapters": state_fm.get("已完成章数", len(chapters)),
        "completed_words": state_fm.get("已完成字数", 0),
        "protagonist": state_fm.get("主角姓名"),
        "last_updated": state_fm.get("最后更新时间"),
        "foreshadowing": get_foreshadowing_stats(root),
    }


def project_risks(project_root: str) -> List[Dict[str, Any]]:
    root = normalize_project_root(project_root)
    inventory = project_inventory(root)
    current_chapter = parse_chapter_number(
        inventory.get("current_chapter") or inventory.get("completed_chapters"),
        default=1,
    )
    risks: List[Dict[str, Any]] = []
    raw_current_chapter = inventory.get("current_chapter")
    if raw_current_chapter not in (None, "") and not isinstance(raw_current_chapter, int) and not str(raw_current_chapter).isdigit():
        risks.append({
            "severity": "warning",
            "type": "invalid_current_chapter",
            "file": "全局写作状态.md",
            "message": f"当前章节不是数字：{raw_current_chapter}",
            "hint": "将 Frontmatter 中的 当前章节 改为数字，例如 15。",
        })
    for item in get_overdue_foreshadowing(root, current_chapter):
        risks.append({
            "severity": "warning",
            "type": "overdue_foreshadowing",
            "file": "伏笔与线索回收池.md",
            "message": f"伏笔 {item['id']} 已到预计回收章节：第{item['expected_chapter']}章",
            "hint": "在下一章细纲或正文中安排回收，或更新预计回收章节。",
        })
    for item in find_unresolved_wikilinks(root):
        risks.append({
            "severity": "error",
            "type": "unresolved_wikilink",
            "file": item["file"],
            "message": item["message"],
            "hint": "创建目标 Markdown 文件，或修正文中的 [[路径/文件名]]。",
        })
    return risks
