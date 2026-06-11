"""
BM25 keyword search over Markdown content with Chinese tokenization.

Builds a search index from Markdown files in the project and supports
keyword queries for pre-writing context retrieval. Pure Python — no
external API keys required.

Index file: .write-novel/search_index.json (regeneratable)
"""

import json
import os
import re
import time
from typing import Any, Dict, List

from rank_bm25 import BM25Okapi

from scripts.encoding_utils import ensure_nfc
from scripts.frontmatter_parser import parse_frontmatter


def _tokenize(text: str) -> List[str]:
    """Tokenize text using jieba for Chinese word segmentation + alphanumeric splitting."""
    tokens = []
    # Split on ASCII word boundaries, keep each segment
    for segment in re.split(r'([a-zA-Z0-9]+)', text):
        segment = segment.strip()
        if not segment:
            continue
        if re.match(r'^[a-zA-Z0-9]+$', segment):
            # Alphanumeric token, lowercase it
            tokens.append(segment.lower())
        else:
            # Chinese segment — use jieba for word segmentation
            try:
                import jieba
                words = jieba.cut(segment)
                tokens.extend(w.strip().lower() for w in words if w.strip())
            except ImportError:
                # Fallback: character-by-character
                tokens.extend(ch for ch in segment if ch.strip())
    return tokens


def _walk_md_files(root: str) -> List[str]:
    """Walk project root and return all .md file paths, excluding derived dirs."""
    result = []
    exclude = {'.write-novel', '.git', '.claude'}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in exclude]
        for fname in filenames:
            if fname.endswith('.md'):
                result.append(os.path.join(dirpath, fname))
    return result


def _extract_searchable_text(filepath: str) -> str:
    """Extract searchable text from a Markdown file."""
    try:
        fm, body = parse_frontmatter(filepath)
    except Exception:
        return ''
    parts = []
    for v in fm.values():
        if isinstance(v, str):
            parts.append(v)
        elif isinstance(v, list):
            parts.extend(str(x) for x in v)
    parts.append(body)
    return '\n'.join(parts)


def build_index(project_root: str) -> Dict[str, Any]:
    """
    Build BM25 search index from all Markdown files in the project.

    Returns:
        {'files': [...], 'corpus': [...], 'tokenized': [[tokens], ...], 'built_at': 'ISO timestamp'}
    """
    root = ensure_nfc(os.path.abspath(project_root))
    md_files = _walk_md_files(root)

    files = []
    corpus = []
    for fpath in md_files:
        text = _extract_searchable_text(fpath)
        if not text.strip():
            continue
        rel = ensure_nfc(os.path.relpath(fpath, root))
        files.append(rel)
        corpus.append(text)

    tokenized = [_tokenize(text) for text in corpus]

    return {
        'files': files,
        'corpus': corpus,
        'tokenized': tokenized,
        'built_at': time.strftime('%Y-%m-%d %H:%M:%S'),
    }


def search(
    project_root: str,
    query: str,
    limit: int = 10,
    reload_if_stale: bool = True,
) -> List[Dict[str, Any]]:
    """
    Search project Markdown files using BM25.

    Args:
        project_root: Project root directory.
        query: Search query string.
        limit: Max results to return.
        reload_if_stale: If True (default), rebuild index if stale.

    Returns list of dicts with 'file', 'score'.
    """
    root = ensure_nfc(os.path.abspath(project_root))

    # Defend against empty queries
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    index_path = ensure_nfc(os.path.join(root, '.write-novel', 'search_index.json'))
    if os.path.isfile(index_path) and (not reload_if_stale or not is_index_stale(root)):
        with open(index_path, 'r', encoding='utf-8') as f:
            cached = json.load(f)
        files = cached['files']
        tokenized = cached['tokenized']
    else:
        data = build_index(root)
        files = data['files']
        tokenized = data['tokenized']

    if not tokenized:
        return []

    bm25 = BM25Okapi(tokenized)
    scores = bm25.get_scores(query_tokens)

    # Filter zero scores before applying limit
    positive = [(i, s) for i, s in enumerate(scores) if s > 0]
    ranked = sorted(positive, key=lambda x: x[1], reverse=True)
    results = []
    for idx, score in ranked[:limit]:
        results.append({
            'file': files[idx],
            'score': round(float(score), 2),
        })
    return results


def search_and_load(
    project_root: str,
    query: str,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """
    Search and return full frontmatter + body for top results.
    Used by skills for pre-writing context injection.
    """
    results = search(project_root, query, limit=limit)
    root = ensure_nfc(os.path.abspath(project_root))
    for r in results:
        fpath = ensure_nfc(os.path.join(root, r['file']))
        try:
            fm, body = parse_frontmatter(fpath)
            r['frontmatter'] = fm
            r['body'] = body[:800]
        except Exception:
            r['frontmatter'] = {}
            r['body'] = ''
    return results


def save_index(project_root: str) -> str:
    """Build and save search index to .write-novel/search_index.json."""
    root = ensure_nfc(os.path.abspath(project_root))
    data = build_index(root)
    out_dir = ensure_nfc(os.path.join(root, '.write-novel'))
    os.makedirs(out_dir, exist_ok=True)
    out_path = ensure_nfc(os.path.join(out_dir, 'search_index.json'))
    save_data = {
        'files': data['files'],
        'tokenized': data['tokenized'],
        'built_at': data['built_at'],
    }
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)
    return out_path


def is_index_stale(project_root: str) -> bool:
    """Check if the index needs rebuilding (older than any source .md file)."""
    root = ensure_nfc(os.path.abspath(project_root))
    index_path = ensure_nfc(os.path.join(root, '.write-novel', 'search_index.json'))
    if not os.path.isfile(index_path):
        return True
    index_mtime = os.path.getmtime(index_path)
    for fpath in _walk_md_files(root):
        if os.path.getmtime(fpath) > index_mtime:
            return True
    return False
