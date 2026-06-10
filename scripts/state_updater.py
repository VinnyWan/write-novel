"""
State updater for the writing continuation closed loop.

After each chapter is generated, this module:
1. Updates 全局写作状态.md frontmatter fields (current chapter, word count)
2. Preserves the user custom area (<!-- USER_AREA_START --> / <!-- USER_AREA_END -->)
3. Creates a backup before writing
4. Updates the volume outline progress
5. Handles chapter file write gate (version suffix on conflict)
"""

import os
import shutil
import time
from typing import Dict, Any, Optional, Tuple
from scripts.encoding_utils import ensure_nfc, safe_open
from scripts.frontmatter_parser import (
    parse_frontmatter,
    parse_frontmatter_string,
)


def backup_file(filepath: str) -> Optional[str]:
    """Create a .bak backup of a file. Returns backup path or None."""
    filepath = ensure_nfc(filepath)
    if not os.path.isfile(filepath):
        return None

    backup_path = filepath + '.bak'
    backup_path = ensure_nfc(backup_path)
    shutil.copy2(filepath, backup_path)
    return backup_path


def update_global_state(
    project_root: str,
    chapter_num: int,
    chapter_word_count: int,
    chapter_title: str = '',
) -> str:
    """
    Update 全局写作状态.md frontmatter after a chapter is completed.

    Updates: 当前章节, 已完成章数, 已完成字数, 最后更新章节, 最后更新时间
    Preserves: all other fields, user custom area
    """
    state_path = ensure_nfc(os.path.join(project_root, '全局写作状态.md'))

    # Create backup
    backup_file(state_path)

    with safe_open(state_path, 'r', encoding='utf-8') as f:
        original = f.read()

    fm, body = parse_frontmatter_string(original)

    # Update progress fields
    fm['当前章节'] = chapter_num + 1
    fm['已完成章数'] = fm.get('已完成章数', 0) + 1
    fm['已完成字数'] = fm.get('已完成字数', 0) + chapter_word_count
    fm['最后更新章节'] = f'第{chapter_num}章'
    fm['最后更新时间'] = time.strftime('%Y-%m-%d %H:%M:%S')

    # Rebuild the file
    new_content = _rebuild_markdown_with_frontmatter(fm, body)

    with safe_open(state_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"[state_updater] 全局写作状态已更新：第{chapter_num}章完成，总字数+{chapter_word_count}")
    return state_path


def update_volume_progress(
    project_root: str,
    volume_num: int,
    chapter_num: int,
    increment: bool = True,
) -> str:
    """
    Update 分卷大纲/第X卷_大纲.md progress.

    Args:
        project_root: Project root directory.
        volume_num: Volume number.
        chapter_num: Chapter number just completed.
        increment: If True, increment completed count. If False, just recalculate.
    """
    vol_path = ensure_nfc(
        os.path.join(project_root, '分卷大纲', f'第{volume_num}卷_大纲.md')
    )

    if not os.path.isfile(vol_path):
        print(f"[state_updater] WARNING: 分卷大纲文件不存在：{vol_path}")
        return ''

    backup_file(vol_path)

    with safe_open(vol_path, 'r', encoding='utf-8') as f:
        original = f.read()

    fm, body = parse_frontmatter_string(original)

    if increment:
        fm['已完成章数'] = fm.get('已完成章数', 0) + 1

    planned = fm.get('计划章数', 1)
    completed = fm.get('已完成章数', 0)
    if planned > 0:
        fm['分卷完成度百分比'] = round(completed / planned * 100, 1)

    # Check volume completion
    if completed >= planned:
        fm['分卷状态'] = '已完成'
        print(f"[state_updater]  第{volume_num}卷已完成！")

    new_content = _rebuild_markdown_with_frontmatter(fm, body)

    with safe_open(vol_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"[state_updater] 第{volume_num}卷进度：{completed}/{planned}（{fm['分卷完成度百分比']}%）")
    return vol_path


def write_chapter_file(
    chapter_body: str,
    chapter_title: str,
    project_root: str,
    chapter_num: int,
) -> str:
    """
    Write a new chapter to 章节草稿/ with conflict handling.

    If file already exists, appends _v{N} suffix instead of overwriting.
    Returns the path to the written file.
    """
    draft_dir = ensure_nfc(os.path.join(project_root, '章节草稿'))
    os.makedirs(draft_dir, exist_ok=True)

    # Clean the title for filename
    safe_title = chapter_title.replace('/', '_').replace('\\', '_').strip()
    if not safe_title:
        safe_title = f'第{chapter_num}章'

    base_path = os.path.join(draft_dir, f'第{chapter_num}章_{safe_title}.md')
    base_path = ensure_nfc(base_path)

    # Conflict resolution: find available version
    final_path = base_path
    version = 1
    while os.path.exists(ensure_nfc(final_path)):
        version += 1
        final_path = ensure_nfc(
            os.path.join(draft_dir, f'第{chapter_num}章_{safe_title}_v{version}.md')
        )

    with safe_open(final_path, 'w', encoding='utf-8') as f:
        f.write(chapter_body)

    if version > 1:
        print(f"[state_updater] 章节文件已存在，写入版本 v{version}：{final_path}")
    else:
        print(f"[state_updater] 章节已写入：{final_path}")

    return final_path


def count_chinese_chars(text: str) -> int:
    """Count Chinese characters in text (excludes whitespace/punctuation)."""
    count = 0
    for ch in text:
        if '一' <= ch <= '鿿' or '㐀' <= ch <= '䶿':
            count += 1
    return count


def run_continuation_loop(
    project_root: str,
    chapter_body: str,
    chapter_title: str,
    chapter_num: int,
    volume_num: int,
) -> Dict[str, str]:
    """
    Run the full continuation closed loop after a chapter is generated.

    1. Write chapter body to 章节草稿/
    2. Generate and save summary (delegates to chapter_summarizer)
    3. Update 全局写作状态.md
    4. Update 分卷大纲/第X卷_大纲.md

    Returns dict with paths of all updated files.
    """
    from scripts.chapter_summarizer import generate_and_save_summary

    result = {}

    # 1. Write chapter
    chapter_path = write_chapter_file(
        chapter_body, chapter_title, project_root, chapter_num
    )
    result['chapter_path'] = chapter_path

    # 2. Generate and save summary
    word_count = count_chinese_chars(chapter_body)
    summary_path = generate_and_save_summary(chapter_body, project_root, chapter_num)
    result['summary_path'] = summary_path

    # 3. Update global state
    update_global_state(project_root, chapter_num, word_count, chapter_title)
    result['state_path'] = os.path.join(project_root, '全局写作状态.md')

    # 4. Update volume progress
    vol_path = update_volume_progress(project_root, volume_num, chapter_num)
    if vol_path:
        result['volume_path'] = vol_path

    return result


# ─── Internal helpers ───────────────────────────────────────

def _rebuild_markdown_with_frontmatter(fm: Dict[str, Any], body: str) -> str:
    """Rebuild a Markdown file with YAML frontmatter and body."""
    import yaml

    # Serialize frontmatter
    fm_lines = []
    for key, value in fm.items():
        if value is None:
            fm_lines.append(f'{key}: ')
        elif isinstance(value, list):
            fm_lines.append(f'{key}:')
            for item in value:
                fm_lines.append(f'  - {item}')
        elif isinstance(value, str) and '\n' in value:
            fm_lines.append(f'{key}: |')
            for line in value.split('\n'):
                fm_lines.append(f'  {line}')
        else:
            fm_lines.append(f'{key}: {value}')

    fm_text = '\n'.join(fm_lines)
    return f'---\n{fm_text}\n---\n\n{body}'
