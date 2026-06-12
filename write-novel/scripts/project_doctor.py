"""
Project health diagnostics, write gates, and projection engine.

Commands:
  doctor     — comprehensive project health check
  preflight  — pre-write readiness check
  write-gate — three-stage validation (pre/during/post chapter commit)
  project    — rebuild all .write-novel/ derived data from Markdown sources

All checks read from Markdown files — this module holds zero state of its own.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional

from scripts.encoding_utils import ensure_nfc
from scripts.frontmatter_parser import parse_frontmatter


REQUIRED_FILES = [
    '全局写作状态.md',
    '伏笔与线索回收池.md',
]

REQUIRED_DIRS = [
    '设定',
    '大纲',
    '正文',
    '追踪',
    '对标',
    '历史章节摘要',
]


def _rel(path: str, root: str) -> str:
    return ensure_nfc(os.path.relpath(path, root))


# ─── Doctor ──────────────────────────────────────────────────

def run_doctor(project_root: str) -> Dict[str, Any]:
    """Comprehensive project health check. Returns {status, checks[], summary{}}."""
    root = ensure_nfc(os.path.abspath(project_root))
    checks: List[Dict[str, str]] = []

    # 1. Required files
    for fname in REQUIRED_FILES:
        fpath = ensure_nfc(os.path.join(root, fname))
        checks.append({
            'name': 'required_file',
            'status': 'ok' if os.path.isfile(fpath) else 'error',
            'path': fname,
            'message': '文件存在' if os.path.isfile(fpath) else '缺少必需文件',
            'hint': '' if os.path.isfile(fpath) else '运行 init 或从模板恢复该文件',
        })

    # 2. Required dirs
    for dname in REQUIRED_DIRS:
        dpath = ensure_nfc(os.path.join(root, dname))
        checks.append({
            'name': 'required_dir',
            'status': 'ok' if os.path.isdir(dpath) else 'error',
            'path': dname,
            'message': '目录存在' if os.path.isdir(dpath) else '缺少必需目录',
            'hint': '' if os.path.isdir(dpath) else '运行 init 或手动创建该目录',
        })

    # 3. Unresolved wikilinks
    for issue in _find_unresolved_wikilinks(root):
        checks.append({
            'name': 'wikilink',
            'status': 'error',
            'path': issue['file'],
            'message': issue['message'],
            'hint': '创建目标文件或修正 Wikilink',
        })

    # 4. Overdue foreshadowing
    for item in _find_overdue_foreshadowing(root):
        checks.append({
            'name': 'foreshadowing',
            'status': 'warning',
            'path': '伏笔与线索回收池.md',
            'message': f"伏笔 {item['id']} 预期第{item['expected_chapter']}章回收（逾期）",
            'hint': '在本章安排回收或调整预期回收章节',
        })

    # 5. Search index staleness
    index_path = ensure_nfc(os.path.join(root, '.write-novel', 'search_index.json'))
    if os.path.isfile(index_path):
        try:
            from scripts.bm25_search import is_index_stale
            stale = is_index_stale(root)
            checks.append({
                'name': 'search_index',
                'status': 'warning' if stale else 'ok',
                'path': '.write-novel/search_index.json',
                'message': '索引已过期，运行 main.py project 重建' if stale else '索引最新',
                'hint': '运行 main.py project' if stale else '',
            })
        except ImportError:
            checks.append({
                'name': 'search_index',
                'status': 'info',
                'path': '.write-novel/search_index.json',
                'message': '搜索索引存在但无法检测过期状态',
                'hint': '',
            })
    else:
        checks.append({
            'name': 'search_index',
            'status': 'info',
            'path': '.write-novel/search_index.json',
            'message': '搜索索引尚未构建',
            'hint': '运行 main.py project 生成',
        })

    # Aggregate status
    status = 'ok'
    if any(c['status'] == 'error' for c in checks):
        status = 'error'
    elif any(c['status'] == 'warning' for c in checks):
        status = 'warning'

    return {
        'project_root': root,
        'status': status,
        'checks': checks,
        'summary': {
            'total': len(checks),
            'ok': sum(1 for c in checks if c['status'] == 'ok'),
            'warning': sum(1 for c in checks if c['status'] == 'warning'),
            'error': sum(1 for c in checks if c['status'] == 'error'),
            'info': sum(1 for c in checks if c['status'] == 'info'),
        },
    }


def format_doctor(result: Dict[str, Any]) -> str:
    lines = [
        '=' * 50,
        '  write-novel 项目健康诊断',
        '=' * 50,
        f"项目: {result['project_root']}",
        f"状态: {result['status']}",
        f"检查: {result['summary']['ok']} ok / {result['summary']['warning']} warning / "
        f"{result['summary']['error']} error / {result['summary']['info']} info",
        '',
    ]
    for c in result['checks']:
        if c['status'] == 'ok':
            continue
        icon = {'error': 'X', 'warning': '!', 'info': 'i'}.get(c['status'], '')
        lines.append(f"[{c['status']}] {icon} {c['path']} — {c['message']}")
        if c.get('hint'):
            lines.append(f"   建议: {c['hint']}")
    lines.append('=' * 50)
    return '\n'.join(lines)


# ─── Preflight ───────────────────────────────────────────────

def preflight(project_root: str, chapter_num: int = 0, volume_num: int = 0) -> Dict[str, Any]:
    """Pre-write readiness check."""
    root = ensure_nfc(os.path.abspath(project_root))
    checks: List[Dict[str, str]] = []

    for fname in REQUIRED_FILES:
        fpath = ensure_nfc(os.path.join(root, fname))
        checks.append({
            'name': fname,
            'status': 'ok' if os.path.isfile(fpath) else 'error',
            'message': '已就绪' if os.path.isfile(fpath) else '文件缺失',
        })

    if volume_num > 0 and chapter_num > 0:
        outline = ensure_nfc(os.path.join(
            root, '大纲', f'第{volume_num}卷_细纲_第{chapter_num}章.md'
        ))
        checks.append({
            'name': '本章细纲',
            'status': 'ok' if os.path.isfile(outline) else 'error',
            'message': '已就绪' if os.path.isfile(outline) else f'缺少第{volume_num}卷第{chapter_num}章细纲',
        })

    try:
        from scripts.bm25_search import is_index_stale
        if is_index_stale(root):
            checks.append({
                'name': 'search_index',
                'status': 'warning',
                'message': '搜索索引过期，检索可能不准确',
            })
    except ImportError:
        pass

    status = 'error' if any(c['status'] == 'error' for c in checks) else \
             'warning' if any(c['status'] == 'warning' for c in checks) else 'ok'

    return {'project_root': root, 'status': status, 'checks': checks}


def format_preflight(result: Dict[str, Any]) -> str:
    lines = ['write-novel preflight', f"项目: {result['project_root']}", f"状态: {result['status']}"]
    for c in result['checks']:
        icon = 'OK' if c['status'] == 'ok' else 'XX' if c['status'] == 'error' else '!!'
        lines.append(f"  [{icon}] {c['name']}: {c['message']}")
    if result['status'] == 'ok':
        lines.append('可以开始写作。')
    return '\n'.join(lines)


# ─── Write Gate ──────────────────────────────────────────────

def write_gate(
    project_root: str,
    stage: str,
    chapter_num: int = 0,
    volume_num: int = 0,
) -> Dict[str, Any]:
    """
    Three-stage write gate validation.
    stage='gate-1': pre-write — outline exists, foreshadowing pool readable
    stage='gate-2': pre-commit — draft exists, review conclusion present
    stage='gate-3': post-commit — commit record, foreshadowing updated, summary present
    """
    root = ensure_nfc(os.path.abspath(project_root))
    gates = {
        'gate-1': _gate1_checks,
        'gate-2': _gate2_checks,
        'gate-3': _gate3_checks,
    }
    if stage not in gates:
        return {'status': 'error', 'message': f'未知 gate: {stage}，可选 gate-1 / gate-2 / gate-3'}
    checks = gates[stage](root, chapter_num, volume_num)
    passed = all(c['status'] == 'ok' for c in checks)
    return {
        'project_root': root,
        'stage': stage,
        'status': 'ok' if passed else 'error',
        'checks': checks,
    }


def _gate1_checks(root: str, chapter_num: int, volume_num: int) -> List[Dict]:
    checks = []
    outline = ensure_nfc(os.path.join(root, '大纲', f'第{volume_num}卷_细纲_第{chapter_num}章.md'))
    checks.append({
        'name': '细纲存在',
        'status': 'ok' if os.path.isfile(outline) else 'error',
        'message': '已就绪' if os.path.isfile(outline) else f'缺少细纲文件',
    })
    fs_pool = ensure_nfc(os.path.join(root, '伏笔与线索回收池.md'))
    checks.append({
        'name': '伏笔池可读',
        'status': 'ok' if os.path.isfile(fs_pool) else 'error',
        'message': '可读' if os.path.isfile(fs_pool) else '伏笔回收池文件缺失',
    })
    return checks


def _gate2_checks(root: str, chapter_num: int, volume_num: int) -> List[Dict]:
    checks = []
    draft = _find_chapter_draft(root, chapter_num)
    checks.append({
        'name': '草稿存在',
        'status': 'ok' if draft else 'error',
        'message': draft or '未找到本章草稿文件',
    })
    if draft:
        fm, _ = parse_frontmatter(draft)
        review_ok = fm.get('审查通过', False)
        checks.append({
            'name': '审查结论',
            'status': 'ok' if review_ok else 'error',
            'message': '审查已通过' if review_ok else '审查未通过或未标记',
        })
    return checks


def _gate3_checks(root: str, chapter_num: int, volume_num: int) -> List[Dict]:
    checks = []
    commit = ensure_nfc(os.path.join(root, '章节提交记录', f'第{chapter_num}章_提交记录.md'))
    checks.append({
        'name': '提交记录',
        'status': 'ok' if os.path.isfile(commit) else 'error',
        'message': '已生成' if os.path.isfile(commit) else '未找到提交记录',
    })
    summary = ensure_nfc(os.path.join(root, '历史章节摘要', f'第{chapter_num}章_摘要.md'))
    checks.append({
        'name': '章节摘要',
        'status': 'ok' if os.path.isfile(summary) else 'error',
        'message': '已生成' if os.path.isfile(summary) else '未找到章节摘要',
    })
    return checks


def format_write_gate(result: Dict[str, Any]) -> str:
    lines = [f"write-gate {result['stage']}: {result['status']}"]
    for c in result['checks']:
        icon = 'OK' if c['status'] == 'ok' else 'XX'
        lines.append(f"  [{icon}] {c['name']}: {c['message']}")
    return '\n'.join(lines)


# ─── Project (projection) ────────────────────────────────────

def run_projection(project_root: str) -> Dict[str, str]:
    """
    Rebuild all .write-novel/ derived data from Markdown sources.
    Returns dict of generated file paths.
    """
    root = ensure_nfc(os.path.abspath(project_root))
    out_dir = ensure_nfc(os.path.join(root, '.write-novel'))
    os.makedirs(out_dir, exist_ok=True)

    result = {}

    # 1. Search index
    try:
        from scripts.bm25_search import save_index
        result['search_index'] = save_index(root)
    except ImportError:
        result['search_index'] = 'ERROR: bm25_search module not available'

    # 2. State aggregation from chapter commits
    state = _build_state_from_commits(root)
    state_path = ensure_nfc(os.path.join(out_dir, 'state.json'))
    with open(state_path, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    result['state'] = state_path

    # 3. Foreshadowing status
    fs_status = _build_foreshadowing_status(root)
    fs_path = ensure_nfc(os.path.join(out_dir, 'foreshadowing_status.json'))
    with open(fs_path, 'w', encoding='utf-8') as f:
        json.dump(fs_status, f, ensure_ascii=False, indent=2)
    result['foreshadowing_status'] = fs_path

    return result


def format_projection(result: Dict[str, str]) -> str:
    lines = ['投影重建完成:']
    for name, path in result.items():
        lines.append(f'  {name}: {path}')
    return '\n'.join(lines)


# ─── Internal helpers ────────────────────────────────────────

def _find_chapter_draft(root: str, chapter_num: int) -> Optional[str]:
    draft_dir = ensure_nfc(os.path.join(root, '正文'))
    if not os.path.isdir(draft_dir):
        return None
    for name in sorted(os.listdir(draft_dir)):
        if name.startswith(f'第{chapter_num}章') and name.endswith('.md'):
            return os.path.join(draft_dir, name)
    return None


def _find_unresolved_wikilinks(root: str) -> List[Dict[str, str]]:
    """Find [[wikilinks]] that reference non-existent files."""
    issues = []
    for dirpath, _, filenames in os.walk(root):
        if '.write-novel' in dirpath or '.git' in dirpath or '.claude' in dirpath:
            continue
        for fname in filenames:
            if not fname.endswith('.md'):
                continue
            fpath = os.path.join(dirpath, fname)
            try:
                _, body = parse_frontmatter(fpath)
            except Exception:
                continue
            for m in re.finditer(r'\[\[([^\]|#]+)', body):
                target = m.group(1).strip()
                if not target.endswith('.md'):
                    target += '.md'
                full = ensure_nfc(os.path.join(root, target))
                if not os.path.isfile(full):
                    issues.append({
                        'file': _rel(fpath, root),
                        'message': f'[[{m.group(1)}]] 未解析 — 目标文件不存在',
                    })
    # Limit to prevent excessive output
    return issues[:50]


def _find_overdue_foreshadowing(root: str) -> List[Dict]:
    """Find foreshadowing entries past expected resolution chapter."""
    fs_path = ensure_nfc(os.path.join(root, '伏笔与线索回收池.md'))
    if not os.path.isfile(fs_path):
        return []

    fm, body = parse_frontmatter(fs_path)
    current_ch = fm.get('当前章节', 0)

    overdue = []
    table_re = re.compile(
        r'^\|\s*(F\d+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(\d+)\s*\|\s*(.*?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|$',
        re.MULTILINE
    )
    for m in table_re.finditer(body):
        fs_id = m.group(1).strip()
        content = m.group(2).strip()
        try:
            expected = int(m.group(5).strip())
        except ValueError:
            continue
        status = m.group(7).strip()
        if '已回收' not in status and current_ch and expected <= current_ch:
            overdue.append({
                'id': fs_id,
                'content': content,
                'expected_chapter': expected,
                'status': status,
            })
    return overdue


def _build_state_from_commits(root: str) -> Dict:
    """Aggregate state from all chapter commit records."""
    commit_dir = ensure_nfc(os.path.join(root, '章节提交记录'))
    if not os.path.isdir(commit_dir):
        return {'chapters': [], 'total_chapters': 0}

    chapters = []
    for fname in sorted(os.listdir(commit_dir)):
        if not fname.endswith('.md'):
            continue
        fpath = ensure_nfc(os.path.join(commit_dir, fname))
        fm, _ = parse_frontmatter(fpath)
        if fm:
            chapters.append({
                'chapter': fm.get('章节'),
                'volume': fm.get('分卷'),
                'timestamp': fm.get('提交时间'),
                'new_characters': fm.get('新增角色', ''),
                'new_locations': fm.get('新增地点', ''),
                'new_concepts': fm.get('新增概念', ''),
                'foreshadowing_planted': fm.get('埋下伏笔', ''),
                'foreshadowing_advanced': fm.get('推进伏笔', ''),
                'foreshadowing_resolved': fm.get('回收伏笔', ''),
                'key_events': fm.get('关键事件', ''),
            })

    return {
        'chapters': chapters,
        'total_chapters': len(chapters),
    }


def _build_foreshadowing_status(root: str) -> Dict:
    """Parse 伏笔与线索回收池.md for current foreshadowing status."""
    fs_path = ensure_nfc(os.path.join(root, '伏笔与线索回收池.md'))
    if not os.path.isfile(fs_path):
        return {'entries': [], 'total': 0, 'resolved': 0, 'developing': 0, 'buried': 0}

    fm, body = parse_frontmatter(fs_path)
    entries = []
    table_re = re.compile(
        r'^\|\s*(F\d+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(\d*)\s*\|\s*(\d*)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|$',
        re.MULTILINE
    )
    for m in table_re.finditer(body):
        entries.append({
            'id': m.group(1).strip(),
            'content': m.group(2).strip(),
            'planted_chapter': m.group(3).strip(),
            'characters': m.group(4).strip(),
            'expected_chapter': int(m.group(5).strip()) if m.group(5).strip() else 0,
            'actual_chapter': int(m.group(6).strip()) if m.group(6).strip() else 0,
            'status': m.group(7).strip(),
            'importance': m.group(8).strip(),
        })

    stats = {
        'total': len(entries),
        'resolved': sum(1 for e in entries if '已回收' in e['status']),
        'developing': sum(1 for e in entries if '发展中' in e['status']),
        'buried': sum(1 for e in entries if '已埋' in e['status']),
    }

    return {'entries': entries, **stats}
