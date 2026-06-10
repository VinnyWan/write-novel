"""
Obsidian-style [[wikilink]] resolver for on-demand dependency loading.

Scans Markdown body text for [[path/filename]] patterns, resolves them to
actual filesystem paths, and loads the target file's frontmatter + body.

Key features:
- Cycle detection: each file loaded at most once per resolution session
- Depth control: default max_depth=1, configurable
- Graceful missing file warnings (doesn't interrupt the pipeline)
- NFC path normalization for cross-platform compatibility
"""

import os
import re
from typing import List, Dict, Set, Optional, Tuple
from scripts.encoding_utils import ensure_nfc, safe_open
from scripts.frontmatter_parser import parse_frontmatter

# Pattern: [[path/filename]] — wikilink with optional display text [[path/file|display]]
_WIKILINK_RE = re.compile(r'\[\[([^\]|#]+?)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]')


def extract_wikilinks(text: str) -> List[str]:
    """
    Extract all wikilink targets from text.

    Returns a list of unique link targets (paths without .md extension).
    Handles [[path/file]], [[path/file|display]], and [[path/file#anchor]].
    """
    matches = _WIKILINK_RE.findall(text)
    # Deduplicate while preserving order
    seen = set()
    result = []
    for m in matches:
        target = m.strip()
        if target not in seen:
            seen.add(target)
            result.append(target)
    return result


def resolve_wikilink_target(link_target: str, project_root: str) -> Optional[str]:
    """
    Resolve a wikilink target to an actual filesystem path.

    Tries:
    1. Exact path: <project_root>/<target>.md
    2. If target doesn't end with .md, append .md
    3. NFC normalization

    Returns the absolute normalized path if file exists, None otherwise.
    """
    if not link_target:
        return None

    # Normalize path separators
    clean_target = link_target.replace('\\', '/').strip('/')

    # Append .md if no extension
    if not clean_target.endswith('.md'):
        clean_target = f'{clean_target}.md'

    full_path = os.path.join(project_root, clean_target)
    full_path = ensure_nfc(full_path)

    if os.path.isfile(full_path):
        return full_path

    return None


def load_linked_file(filepath: str) -> Dict:
    """
    Load a linked file's frontmatter and body.

    Returns a dict with:
        path: absolute path
        frontmatter: dict of frontmatter fields
        body: markdown body text
    """
    fm, body = parse_frontmatter(filepath)
    return {
        'path': filepath,
        'frontmatter': fm,
        'body': body,
    }


def resolve_wikilinks(
    text: str,
    project_root: str,
    max_depth: int = 1,
    _loaded: Optional[Set[str]] = None,
    _depth: int = 0,
) -> List[Dict]:
    """
    Resolve all wikilinks in text, loading linked files.

    Args:
        text: Markdown body text to scan for [[wikilinks]]
        project_root: Root directory of the project
        max_depth: Maximum nesting depth for recursive resolution (default 1)
        _loaded: Internal set of already-loaded paths (for cycle protection)
        _depth: Internal depth counter

    Returns:
        List of dicts with path, frontmatter, body for each resolved file.
    """
    if _loaded is None:
        _loaded = set()

    results = []
    links = extract_wikilinks(text)

    for target in links:
        filepath = resolve_wikilink_target(target, project_root)

        if filepath is None:
            print(f"[wikilink_resolver] WARNING: Unresolved link [[{target}]] — file not found")
            continue

        if filepath in _loaded:
            # Already loaded in this session — cycle protection
            continue

        _loaded.add(filepath)
        file_data = load_linked_file(filepath)
        results.append(file_data)

        # Recursively resolve links in the loaded file's body (depth-limited)
        if _depth < max_depth:
            nested = resolve_wikilinks(
                file_data['body'],
                project_root,
                max_depth=max_depth,
                _loaded=_loaded,
                _depth=_depth + 1,
            )
            results.extend(nested)

    return results


def collect_linked_frontmatter(
    text: str,
    project_root: str,
    max_depth: int = 1,
) -> Dict[str, Dict]:
    """
    Convenience function: collect linked files' frontmatter keyed by relative path.

    Returns: {relative_path: frontmatter_dict}
    """
    loaded = resolve_wikilinks(text, project_root, max_depth=max_depth)
    result = {}
    for item in loaded:
        rel_path = os.path.relpath(item['path'], project_root)
        # Use NFC-normalized relative path as key
        rel_path = ensure_nfc(rel_path)
        result[rel_path] = item['frontmatter']
    return result


def collect_linked_bodies(
    text: str,
    project_root: str,
    max_depth: int = 1,
) -> Dict[str, str]:
    """
    Convenience function: collect linked files' bodies keyed by relative path.

    Returns: {relative_path: body_text}
    """
    loaded = resolve_wikilinks(text, project_root, max_depth=max_depth)
    result = {}
    for item in loaded:
        rel_path = os.path.relpath(item['path'], project_root)
        rel_path = ensure_nfc(rel_path)
        result[rel_path] = item['body']
    return result
