"""
XML-structured Prompt builder for web novel writing.

Assembles multiple Markdown source files into a tightly-structured XML prompt
that guides the LLM's chapter generation. Uses Chinese XML tags for clarity.

Key sections:
- <全局核心设定>: world setting + protagonist state
- <本卷宏观主线>: current volume arc
- <前情提要>: recent 20 chapter summaries + last chapter ending + skeleton
- <本章硬性剧本任务>: current chapter outline tasks
- <写作约束与高压线>: system prompts + banned words + foreshadowing alerts
- <参考文件>: files loaded via [[wikilinks]]
"""

import os
import re
import glob
from typing import List, Dict, Optional, Tuple
from scripts.encoding_utils import ensure_nfc, safe_open
from scripts.frontmatter_parser import parse_frontmatter, extract_user_area
from scripts.wikilink_resolver import resolve_wikilinks


def read_file_text(filepath: str) -> Optional[str]:
    """Read a file's full text content, or return None if not found."""
    try:
        with safe_open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None


def build_global_settings(project_root: str) -> str:
    """Build <全局核心设定> section from global state + world setting + protagonist."""
    parts = []

    # 1. Global writing state
    state_path = os.path.join(project_root, '全局写作状态.md')
    state_fm, state_body = parse_frontmatter(state_path)
    if state_fm:
        parts.append('<主角当前状态>')
        parts.append(f'  主角姓名：{state_fm.get("主角姓名", "")}')
        parts.append(f'  当前境界：{state_fm.get("主角当前境界", "")}')
        parts.append(f'  当前位置：{state_fm.get("主角当前位置", "")}')
        parts.append(f'  当前章节：第{state_fm.get("当前章节", "")}章')
        parts.append('</主角当前状态>')

    # 2. World setting
    ws_path = os.path.join(project_root, '世界设定', '世界观.md')
    ws_fm = {}
    if os.path.isfile(ensure_nfc(ws_path)):
        ws_fm, _ = parse_frontmatter(ws_path)
    # Fallback to template
    if not ws_fm:
        ws_path2 = os.path.join(project_root, '世界设定模板.md')
        if os.path.isfile(ensure_nfc(ws_path2)):
            ws_fm, _ = parse_frontmatter(ws_path2)

    if ws_fm:
        parts.append('<世界观概要>')
        parts.append(f'  世界观名称：{ws_fm.get("世界观名称", "")}')
        parts.append(f'  力量体系类型：{ws_fm.get("力量体系类型", "")}')
        parts.append(f'  时代背景：{ws_fm.get("时代背景", "")}')
        parts.append('</世界观概要>')

    return '\n'.join(parts)


def build_volume_mainline(project_root: str, volume_num: int) -> str:
    """Build <本卷宏观主线> section from volume outline."""
    vol_path = ensure_nfc(
        os.path.join(project_root, '分卷大纲', f'第{volume_num}卷_大纲.md')
    )
    _, body = parse_frontmatter(vol_path)

    # Extract 分卷主线 section
    mainline = _extract_section(body, '分卷主线')
    turning_points = _extract_section(body, '关键转折点')

    parts = []
    if mainline:
        parts.append(f'<第{volume_num}卷主线>{mainline}</第{volume_num}卷主线>')
    if turning_points:
        parts.append(f'<关键转折点>{turning_points}</关键转折点>')

    return '\n'.join(parts)


def build_recent_summaries(project_root: str, current_chapter: int) -> str:
    """
    Build <前情提要> section.

    Includes:
    - Recent 20 chapters' full summaries (~200 chars each)
    - Last chapter's ending text (200 chars)
    - Older chapters' skeleton (1 per 20 chapters, ≤20 chars each)
    """
    summaries_dir = ensure_nfc(os.path.join(project_root, '历史章节摘要'))
    parts = []

    # Recent 20 chapter summaries
    start_ch = max(1, current_chapter - 20)
    recent_parts = []
    for ch in range(start_ch, current_chapter):
        summary_file = os.path.join(summaries_dir, f'第{ch}章_摘要.md')
        if os.path.isfile(ensure_nfc(summary_file)):
            _, body = parse_frontmatter(summary_file)
            recent_parts.append(f'  <第{ch}章摘要>{body.strip()[:200]}</第{ch}章摘要>')

    if recent_parts:
        parts.append('<近期章节摘要>')
        parts.extend(recent_parts)
        parts.append('</近期章节摘要>')

    # Last chapter ending text (200 chars)
    prev_chapter = current_chapter - 1
    if prev_chapter > 0:
        # Search for the previous chapter file
        draft_dir = ensure_nfc(os.path.join(project_root, '章节草稿'))
        prev_path = _find_chapter_file(draft_dir, prev_chapter)
        if prev_path:
            _, body = parse_frontmatter(prev_path)
            ending = body.strip()[-200:] if len(body) > 200 else body.strip()
            parts.append(f'<上一章结尾>{ending}</上一章结尾>')

    # Skeleton sampling for older chapters (1 per 20 chapters, ≤20 chars)
    if current_chapter > 20:
        skeleton_parts = []
        for ch in range(1, start_ch, 20):
            summary_file = os.path.join(summaries_dir, f'第{ch}章_摘要.md')
            if os.path.isfile(ensure_nfc(summary_file)):
                _, body = parse_frontmatter(summary_file)
                skeleton = body.strip()[:20]
                skeleton_parts.append(f'  第{ch}章：{skeleton}')

        if skeleton_parts:
            parts.append('<骨骼摘要>')
            parts.extend(skeleton_parts)
            parts.append('</骨骼摘要>')

    return '\n'.join(parts)


def build_chapter_tasks(project_root: str, volume_num: int, chapter_num: int) -> str:
    """Build <本章硬性剧本任务> from chapter outline."""
    outline_path = ensure_nfc(
        os.path.join(project_root, '分卷大纲', f'第{volume_num}卷_细纲_第{chapter_num}章.md')
    )
    # Fallback: check 章节草稿 directory
    if not os.path.isfile(outline_path):
        draft_dir = ensure_nfc(os.path.join(project_root, '章节草稿'))
        fallback = _find_chapter_file(draft_dir, chapter_num)
        if fallback:
            outline_path = fallback

    if not os.path.isfile(outline_path):
        return '<本章硬性剧本任务>未找到细纲文件</本章硬性剧本任务>'

    fm, body = parse_frontmatter(outline_path)

    parts = []
    parts.append('<本章硬性剧本任务>')

    # Frontmatter metadata
    if fm:
        parts.append(f'  <核心冲突>{fm.get("本章核心冲突", "")}</核心冲突>')
        parts.append(f'  <期待感钩子>{fm.get("期待感钩子", "")}</期待感钩子>')
        parts.append(f'  <字数预期>{fm.get("字数预期", "")}</字数预期>')

        characters = fm.get('出场角色', [])
        if characters:
            chars_str = '、'.join(characters) if isinstance(characters, list) else str(characters)
            parts.append(f'  <出场角色>{chars_str}</出场角色>')

    # Body hard tasks
    tasks = _extract_section(body, '本章硬性剧本任务')
    if tasks:
        parts.append(f'  <硬性任务>\n{tasks}\n  </硬性任务>')

    parts.append('</本章硬性剧本任务>')
    return '\n'.join(parts)


def build_constraints(project_root: str, current_chapter: int) -> str:
    """Build <写作约束与高压线> from global writing state."""
    state_path = os.path.join(project_root, '全局写作状态.md')
    _, body = parse_frontmatter(state_path)

    parts = []
    parts.append('<写作约束与高压线>')

    # System prompt section
    sys_prompt = _extract_section(body, '全局系统提示词')
    if sys_prompt:
        parts.append(f'  <全局系统提示词>\n{sys_prompt}\n  </全局系统提示词>')

    # Banned words
    banned = _extract_section(body, '高压线禁用词')
    if banned:
        parts.append(f'  <高压线禁用词>\n{banned}\n  </高压线禁用词>')

    # Foreshadowing alerts from pool
    foreshadowing_path = os.path.join(project_root, '伏笔与线索回收池.md')
    if os.path.isfile(ensure_nfc(foreshadowing_path)):
        _, fs_body = parse_frontmatter(foreshadowing_path)
        overdue = _find_overdue_foreshadowing(fs_body, current_chapter)
        if overdue:
            parts.append('  <伏笔回收提醒>')
            parts.append('    以下伏笔已超过预计回收章节，请在本章考虑回收：')
            for item in overdue:
                parts.append(f'    - [{item["id"]}] {item["content"]}（预计第{item["expected"]}章回收）')
            parts.append('  </伏笔回收提醒>')

    parts.append('</写作约束与高压线>')
    return '\n'.join(parts)


def build_reference_section(text: str, project_root: str, max_depth: int = 1) -> str:
    """Build <参考文件> section from [[wikilinks]] in text."""
    loaded = resolve_wikilinks(text, project_root, max_depth=max_depth)

    if not loaded:
        return '<参考文件>无</参考文件>'

    parts = []
    parts.append('<参考文件>')
    for item in loaded:
        rel_path = os.path.relpath(item['path'], project_root)
        parts.append(f'  <文件 路径="{rel_path}">')
        # Include key frontmatter fields as summary
        if item['frontmatter']:
            for key, val in item['frontmatter'].items():
                if val is not None and val != '' and val != []:
                    parts.append(f'    <字段 名称="{key}">{val}</字段>')
        # Include body (truncated if very long)
        body_text = item['body'].strip()[:500]
        if body_text:
            parts.append(f'    <正文>{body_text}</正文>')
        parts.append(f'  </文件>')

    parts.append('</参考文件>')
    return '\n'.join(parts)


def assemble_prompt(
    project_root: str,
    volume_num: int,
    chapter_num: int,
    max_wikilink_depth: int = 1,
) -> str:
    """
    Main entry point: assemble the complete XML prompt for generating a chapter.

    Args:
        project_root: Root directory of the book project.
        volume_num: Current volume number.
        chapter_num: Current chapter number within the volume.
        max_wikilink_depth: Max depth for wikilink resolution.

    Returns:
        Complete XML prompt string ready to send to the LLM.
    """
    # Collect all texts that may contain wikilinks
    state_path = os.path.join(project_root, '全局写作状态.md')
    _, state_body = parse_frontmatter(state_path)

    outline_path = ensure_nfc(
        os.path.join(project_root, '分卷大纲', f'第{volume_num}卷_细纲_第{chapter_num}章.md')
    )
    outline_body = ''
    if os.path.isfile(outline_path):
        _, outline_body = parse_frontmatter(outline_path)

    all_text_for_links = state_body + '\n' + outline_body

    parts = []
    parts.append('<写书Prompt>')
    parts.append('')
    parts.append('<全局核心设定>')
    parts.append(build_global_settings(project_root))
    parts.append('</全局核心设定>')
    parts.append('')
    parts.append('<本卷宏观主线>')
    parts.append(build_volume_mainline(project_root, volume_num))
    parts.append('</本卷宏观主线>')
    parts.append('')
    parts.append('<前情提要>')
    parts.append(build_recent_summaries(project_root, chapter_num))
    parts.append('</前情提要>')
    parts.append('')
    parts.append(build_chapter_tasks(project_root, volume_num, chapter_num))
    parts.append('')
    parts.append(build_constraints(project_root, chapter_num))
    parts.append('')
    parts.append(build_reference_section(all_text_for_links, project_root, max_wikilink_depth))
    parts.append('')
    parts.append('</写书Prompt>')

    return '\n'.join(parts)


def save_prompt(prompt: str, project_root: str) -> str:
    """Save the assembled prompt to 当前Prompt.xml in the project root."""
    output_path = ensure_nfc(os.path.join(project_root, '当前Prompt.xml'))
    with safe_open(output_path, 'w', encoding='utf-8') as f:
        f.write(prompt)
    return output_path


# ─── Internal helpers ───────────────────────────────────────

def _extract_section(body: str, heading: str) -> Optional[str]:
    """
    Extract content under a Markdown ## heading.

    Returns the text between the heading and the next ## heading (or end of file),
    with the heading line removed.
    """
    pattern = rf'^##\s+{re.escape(heading)}\s*\n(.*?)(?=^##\s|\Z)'
    match = re.search(pattern, body, re.DOTALL | re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None


def _find_chapter_file(directory: str, chapter_num: int) -> Optional[str]:
    """Find a chapter file by chapter number in a directory."""
    directory = ensure_nfc(directory)
    if not os.path.isdir(directory):
        return None

    for entry in os.listdir(directory):
        entry_path = os.path.join(directory, entry)
        if os.path.isfile(entry_path) and entry.startswith(f'第{chapter_num}章'):
            return entry_path

    return None


def _find_overdue_foreshadowing(body: str, current_chapter: int) -> List[Dict]:
    """
    Find foreshadowing entries that are overdue for resolution.

    Scans the Markdown table in 伏笔与线索回收池.md for entries where:
    - Status is not '🟢已回收'
    - Expected resolution chapter is <= current_chapter
    """
    overdue = []
    # Parse Markdown table rows
    table_row_re = re.compile(
        r'^\|\s*(F\d+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(\d+)\s*\|\s*(\d*)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|$',
        re.MULTILINE
    )
    for match in table_row_re.finditer(body):
        fs_id = match.group(1)
        content = match.group(2).strip()
        expected_ch = int(match.group(5)) if match.group(5) else 0
        status = match.group(7).strip()

        if '已回收' not in status and expected_ch > 0 and expected_ch <= current_chapter:
            overdue.append({
                'id': fs_id,
                'content': content,
                'expected': expected_ch,
                'status': status,
            })

    return overdue
