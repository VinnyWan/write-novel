"""
Foreshadowing (伏笔) lifecycle tracker.

Manages the full lifecycle of foreshadowing elements:
- Registration: new foreshadowing from chapter outlines or summaries
- Advancement: 🟡已埋 → 🟠发展中 when referenced in later chapters
- Resolution: → 🟢已回收 when resolved
- Overdue alerts: when current chapter exceeds expected resolution chapter

Operates on 伏笔与线索回收池.md using Markdown table parsing and rewriting.
"""

import os
import re
from typing import List, Dict, Optional, Tuple
from scripts.encoding_utils import ensure_nfc, safe_open
from scripts.frontmatter_parser import parse_frontmatter, parse_frontmatter_string


# Foreshadowing status states
STATUS_BURIED = '🟡已埋'
STATUS_DEVELOPING = '🟠发展中'
STATUS_RESOLVED = '🟢已回收'


def _next_fs_id(fm: Dict) -> str:
    """Generate the next foreshadowing ID (F001, F002, ...)."""
    total = fm.get('总伏笔数', 0)
    return f'F{total + 1:03d}'


def register_new_foreshadowing(
    project_root: str,
    fs_content: str,
    chapter_num: int,
    related_characters: str = '',
    expected_resolve_chapter: int = 0,
    importance: str = '中',
) -> Optional[str]:
    """
    Register a new foreshadowing in 伏笔与线索回收池.md.

    Args:
        project_root: Project root directory.
        fs_content: Description of the foreshadowing.
        chapter_num: The chapter where this foreshadowing is planted.
        related_characters: Comma-separated character names.
        expected_resolve_chapter: Expected chapter for resolution (0 = unknown).
        importance: Importance level (高/中/低).

    Returns:
        The new foreshadowing ID (e.g., 'F005'), or None on failure.
    """
    fs_path = ensure_nfc(os.path.join(project_root, '伏笔与线索回收池.md'))

    if not os.path.isfile(fs_path):
        print(f"[foreshadowing_tracker] ERROR: 伏笔回收池文件不存在：{fs_path}")
        return None

    # Read current file
    fm, body = parse_frontmatter(fs_path)
    new_id = _next_fs_id(fm)

    # Build new table row
    resolve_ch_str = str(expected_resolve_chapter) if expected_resolve_chapter > 0 else ''
    new_row = (
        f'| {new_id} | {fs_content} | 第{chapter_num}章 | {related_characters} | '
        f'{resolve_ch_str} | | {STATUS_BURIED} | {importance} |'
    )

    # Insert the new row into the table (after the header separator row)
    lines = body.split('\n')
    insert_idx = _find_table_insert_point(lines)
    if insert_idx is None:
        print("[foreshadowing_tracker] ERROR: 无法定位伏笔表格插入点")
        return None

    lines.insert(insert_idx, new_row)

    # Update frontmatter counters
    fm['总伏笔数'] = fm.get('总伏笔数', 0) + 1
    fm['最后更新时间'] = _current_timestamp()

    # Write back
    _write_fs_file(fs_path, fm, '\n'.join(lines))

    print(f"[foreshadowing_tracker] 新伏笔已注册：{new_id} — {fs_content[:30]}...")
    return new_id


def advance_foreshadowing(
    project_root: str,
    fs_ids: List[str],
) -> int:
    """
    Advance foreshadowing state: 🟡已埋 → 🟠发展中.

    Used when a later chapter's outline references an existing foreshadowing.

    Args:
        project_root: Project root directory.
        fs_ids: List of foreshadowing IDs to advance.

    Returns:
        Number of successfully advanced entries.
    """
    fs_path = ensure_nfc(os.path.join(project_root, '伏笔与线索回收池.md'))

    if not os.path.isfile(fs_path):
        return 0

    fm, body = parse_frontmatter(fs_path)
    lines = body.split('\n')
    advanced = 0

    for i, line in enumerate(lines):
        for fs_id in fs_ids:
            if f'| {fs_id} |' in line and STATUS_BURIED in line:
                lines[i] = line.replace(STATUS_BURIED, STATUS_DEVELOPING)
                advanced += 1
                print(f"[foreshadowing_tracker] 伏笔状态推进：{fs_id} → {STATUS_DEVELOPING}")
                break

    if advanced > 0:
        fm['发展中数'] = fm.get('发展中数', 0) + advanced
        fm['最后更新时间'] = _current_timestamp()

    _write_fs_file(fs_path, fm, '\n'.join(lines))
    return advanced


def resolve_foreshadowing(
    project_root: str,
    fs_ids: List[str],
    chapter_num: int,
) -> int:
    """
    Mark foreshadowing as resolved: → 🟢已回收.

    Args:
        project_root: Project root directory.
        fs_ids: List of foreshadowing IDs to resolve.
        chapter_num: The chapter where resolution occurs.

    Returns:
        Number of successfully resolved entries.
    """
    fs_path = ensure_nfc(os.path.join(project_root, '伏笔与线索回收池.md'))

    if not os.path.isfile(fs_path):
        return 0

    fm, body = parse_frontmatter(fs_path)
    lines = body.split('\n')
    resolved = 0

    for i, line in enumerate(lines):
        for fs_id in fs_ids:
            if f'| {fs_id} |' in line:
                # Update status
                for old_status in [STATUS_BURIED, STATUS_DEVELOPING]:
                    if old_status in line:
                        lines[i] = line.replace(old_status, STATUS_RESOLVED)
                        break

                # Update actual resolve chapter column (col 5 = 实际回收章节)
                lines[i] = _set_table_column(lines[i], 5, str(chapter_num))

                resolved += 1
                print(f"[foreshadowing_tracker] 伏笔已回收：{fs_id}（第{chapter_num}章）")
                break

    if resolved > 0:
        fm['已回收数'] = fm.get('已回收数', 0) + resolved
        fm['发展中数'] = max(0, fm.get('发展中数', 0) - resolved)
        fm['最后更新时间'] = _current_timestamp()

    _write_fs_file(fs_path, fm, '\n'.join(lines))
    return resolved


def scan_and_advance_from_outline(
    project_root: str,
    outline_body: str,
) -> int:
    """
    Scan a chapter outline for referenced foreshadowing IDs and advance them.

    Returns number of advanced entries.
    """
    # Find lines containing foreshadowing references, then extract all F\d{3} IDs
    ref_lines = re.findall(r'(?:关联伏笔|伏笔)\s*[:：]\s*(.+)', outline_body)
    refs = []
    for line in ref_lines:
        refs.extend(re.findall(r'F\d{3}', line))
    refs += re.findall(r'\[\[伏笔与线索/(F\d{3})\]\]', outline_body)

    if not refs:
        return 0

    return advance_foreshadowing(project_root, list(set(refs)))


def scan_and_resolve_from_summary(
    project_root: str,
    summary_body: str,
    chapter_num: int,
) -> int:
    """
    Scan chapter summary for resolved foreshadowing markers and mark them resolved.

    Returns number of resolved entries.
    """
    resolved = re.findall(r'回收伏笔\[(F\d{3})\]', summary_body)
    if not resolved:
        return 0

    return resolve_foreshadowing(project_root, list(set(resolved)), chapter_num)


def scan_and_register_from_text(
    project_root: str,
    text: str,
    chapter_num: int,
) -> List[str]:
    """
    Scan text (outline or body) for new foreshadowing markers and register them.

    Format: 伏笔[Fxxx]: content description
    If the Fxxx ID is new, register it. If it exists, skip.

    Returns list of newly registered IDs.
    """
    markers = re.findall(r'伏笔\[(F\d{3})\][：:]\s*(.+?)(?:[。\n]|$)', text)
    if not markers:
        return []

    # Check existing IDs
    fs_path = ensure_nfc(os.path.join(project_root, '伏笔与线索回收池.md'))
    if os.path.isfile(fs_path):
        _, body = parse_frontmatter(fs_path)
        existing = set(re.findall(r'F\d{3}', body))
    else:
        existing = set()

    new_ids = []
    for fs_id, content in markers:
        if fs_id not in existing:
            # This is a new foreshadowing defined inline
            registered = register_new_foreshadowing(
                project_root, content.strip(), chapter_num
            )
            if registered:
                new_ids.append(registered)

    return new_ids


def get_overdue_foreshadowing(
    project_root: str,
    current_chapter: int,
) -> List[Dict]:
    """
    Get list of foreshadowing entries past their expected resolution chapter.

    Returns list of dicts with id, content, expected_chapter, status.
    """
    fs_path = ensure_nfc(os.path.join(project_root, '伏笔与线索回收池.md'))
    if not os.path.isfile(fs_path):
        return []

    _, body = parse_frontmatter(fs_path)
    overdue = []

    table_row_re = re.compile(
        r'^\|\s*(F\d+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(\d+)\s*\|\s*(.*?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|$',
        re.MULTILINE
    )

    for match in table_row_re.finditer(body):
        fs_id = match.group(1)
        content = match.group(2).strip()
        expected_ch_str = match.group(5).strip()
        status = match.group(7).strip()

        if not expected_ch_str:
            continue

        expected_ch = int(expected_ch_str)

        if '已回收' not in status and expected_ch <= current_chapter:
            overdue.append({
                'id': fs_id,
                'content': content,
                'expected_chapter': expected_ch,
                'status': status,
            })

    return overdue


def get_foreshadowing_stats(project_root: str) -> Dict:
    """Get statistics from the foreshadowing pool."""
    fs_path = ensure_nfc(os.path.join(project_root, '伏笔与线索回收池.md'))
    if not os.path.isfile(fs_path):
        return {'total': 0, 'resolved': 0, 'developing': 0, 'buried': 0}

    fm, _ = parse_frontmatter(fs_path)
    return {
        'total': fm.get('总伏笔数', 0),
        'resolved': fm.get('已回收数', 0),
        'developing': fm.get('发展中数', 0),
        'buried': fm.get('总伏笔数', 0) - fm.get('已回收数', 0) - fm.get('发展中数', 0),
    }


# ─── Internal helpers ───────────────────────────────────────

def _find_table_insert_point(lines: List[str]) -> Optional[int]:
    """
    Find where to insert a new row in the Markdown table.
    Returns the line index AFTER which to insert (i.e., used as insert position).
    Inserts after the table header separator (|---|---|...|).
    """
    for i, line in enumerate(lines):
        if re.match(r'^\|[\s\-|]+\|', line):
            # Found the header separator. Insert after next line if it's the
            # placeholder row (F001), otherwise insert after separator +1
            return i + 1
    return None


def _set_table_column(line: str, col_idx: int, value: str) -> str:
    """Set column value in table row using simple split/join (no strip)."""
    parts = line.split('|')
    # parts[0] is empty (before first |), data cols start at parts[1]
    target = col_idx + 1
    if target < len(parts) - 1:
        old = parts[target].strip()
        if old:
            parts[target] = parts[target].replace(old, str(value), 1)
        else:
            parts[target] = ' ' + str(value) + ' '
    return '|'.join(parts)


def _write_fs_file(filepath: str, fm: Dict, body: str):
    """Write foreshadowing pool file with updated frontmatter and body."""
    from scripts.state_updater import backup_file
    from scripts.state_updater import _rebuild_markdown_with_frontmatter

    backup_file(filepath)
    new_content = _rebuild_markdown_with_frontmatter(fm, body)

    with safe_open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)


def _current_timestamp() -> str:
    """Get current timestamp string."""
    import time
    return time.strftime('%Y-%m-%d %H:%M:%S')


def run_foreshadowing_pipeline(
    project_root: str,
    outline_body: str,
    summary_body: str,
    chapter_num: int,
) -> Dict:
    """
    Run the complete foreshadowing pipeline for a chapter.

    1. Register new foreshadowing from outline
    2. Advance referenced foreshadowing
    3. Resolve foreshadowing from summary
    4. Check overdue

    Returns summary dict of actions taken.
    """
    result = {
        'registered': [],
        'advanced': 0,
        'resolved': 0,
        'overdue': [],
    }

    # 1. Register new
    result['registered'] = scan_and_register_from_text(
        project_root, outline_body, chapter_num
    )

    # 2. Advance
    result['advanced'] = scan_and_advance_from_outline(
        project_root, outline_body
    )

    # 3. Resolve
    result['resolved'] = scan_and_resolve_from_summary(
        project_root, summary_body, chapter_num
    )

    # 4. Check overdue
    result['overdue'] = get_overdue_foreshadowing(project_root, chapter_num)

    return result
