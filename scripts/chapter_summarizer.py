"""
Chapter summarizer: generates ~200-character event and foreshadowing summaries.

Extracts key information from a newly written chapter and generates a
structured summary that includes: core events, character changes, new
foreshadowing planted, and foreshadowing resolved.
"""

import re
import os
from typing import Dict, Optional, Tuple
from scripts.encoding_utils import ensure_nfc, safe_open
from scripts.frontmatter_parser import parse_frontmatter, parse_frontmatter_string


def generate_summary(chapter_body: str) -> Dict[str, str]:
    """
    Analyze chapter body and generate a structured summary.

    Args:
        chapter_body: Full text of the chapter.

    Returns:
        Dict with keys: events, character_changes, new_foreshadowing,
        resolved_foreshadowing, full_summary
    """
    # Extract sentences for analysis
    sentences = _split_sentences(chapter_body)

    # Detect key events (first 3 significant narrative shifts)
    events = _extract_key_events(sentences)

    # Detect character mentions and potential state changes
    character_changes = _detect_character_changes(chapter_body)

    # Detect foreshadowing markers
    new_foreshadowing = _detect_new_foreshadowing(chapter_body)
    resolved_foreshadowing = _detect_resolved_foreshadowing(chapter_body)

    # Build full summary (~200 chars)
    summary_parts = []
    if events:
        summary_parts.append(f'核心事件：{";".join(events[:3])}')
    if character_changes:
        summary_parts.append(f'角色变化：{character_changes}')
    if new_foreshadowing:
        summary_parts.append(f'新埋伏笔：{";".join(new_foreshadowing[:2])}')
    if resolved_foreshadowing:
        summary_parts.append(f'回收伏笔：{";".join(resolved_foreshadowing[:2])}')

    full_summary = '。'.join(summary_parts) + '。'

    return {
        'events': '; '.join(events[:3]),
        'character_changes': character_changes or '无显著变化',
        'new_foreshadowing': '; '.join(new_foreshadowing),
        'resolved_foreshadowing': '; '.join(resolved_foreshadowing),
        'full_summary': full_summary,
    }


def write_summary(
    summary_dict: Dict[str, str],
    project_root: str,
    chapter_num: int,
) -> str:
    """
    Write the chapter summary to 历史章节摘要/第N章_摘要.md.

    Returns the path to the written summary file.
    """
    summary_dir = ensure_nfc(os.path.join(project_root, '历史章节摘要'))
    os.makedirs(summary_dir, exist_ok=True)

    summary_file = os.path.join(summary_dir, f'第{chapter_num}章_摘要.md')
    summary_file = ensure_nfc(summary_file)

    content = f"""---
章节序号: {chapter_num}
核心事件: {summary_dict['events']}
角色变化: {summary_dict['character_changes']}
新埋伏笔: {summary_dict.get('new_foreshadowing', '')}
已回收伏笔: {summary_dict.get('resolved_foreshadowing', '')}
---

# 第{chapter_num}章摘要

{summary_dict['full_summary']}
"""
    with safe_open(summary_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"[chapter_summarizer] 摘要已写入：{summary_file}")
    return summary_file


def generate_and_save_summary(
    chapter_body: str,
    project_root: str,
    chapter_num: int,
) -> str:
    """Convenience function: generate summary and write to file."""
    summary = generate_summary(chapter_body)
    return write_summary(summary, project_root, chapter_num)


# ─── Internal helpers ───────────────────────────────────────

def _split_sentences(text: str) -> list:
    """Split Chinese text into sentences."""
    # Split on Chinese punctuation
    parts = re.split(r'[。！？；\n]+', text)
    return [p.strip() for p in parts if len(p.strip()) > 5]


def _extract_key_events(sentences: list) -> list:
    """Extract key event sentences (first 3 substantive ones)."""
    events = []
    for s in sentences[:min(10, len(sentences))]:
        if len(s) > 10:
            events.append(s[:40] + ('...' if len(s) > 40 else ''))
        if len(events) >= 3:
            break
    return events


def _detect_character_changes(text: str) -> str:
    """Detect character state changes from chapter text."""
    changes = []

    # Pattern: character advancement
    breakthrough_re = re.findall(r'(\S{2,4})突破[了到至达](\S+)', text)
    for name, level in breakthrough_re[:2]:
        changes.append(f'{name}突破至{level}')

    # Pattern: character death/injury
    death_re = re.findall(r'(\S{2,4})(身亡|陨落|重伤|昏迷)', text)
    for name, event in death_re[:2]:
        changes.append(f'{name}{event}')

    # Pattern: character departure/arrival
    travel_re = re.findall(r'(\S{2,4})(离开|到达|进入)(\S{2,6})', text)
    for name, action, place in travel_re[:2]:
        changes.append(f'{name}{action}{place}')

    return '；'.join(changes) if changes else '无显著变化'


def _detect_new_foreshadowing(text: str) -> list:
    """Detect new foreshadowing markers in chapter text."""
    # Look for explicit 伏笔 markers
    markers = re.findall(r'伏笔\[(F\d+)\][：:]\s*(.+?)(?:[。\n]|$)', text)
    if markers:
        return [f'{m[0]}: {m[1][:30]}' for m in markers]

    # Heuristic: sentences with "隐约/似乎/仿佛" suggest foreshadowing
    hint_sentences = re.findall(
        r'([^。！？\n]{0,20}(?:隐约|似乎|仿佛|暗自|心中暗道|预感)[^。！？\n]{0,30})',
        text
    )
    return [s[:40] for s in hint_sentences[:3]]


def _detect_resolved_foreshadowing(text: str) -> list:
    """Detect resolved foreshadowing markers."""
    markers = re.findall(r'回收伏笔\[(F\d+)\]', text)
    return markers
