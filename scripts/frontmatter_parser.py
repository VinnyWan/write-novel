"""
High-tolerance Markdown Frontmatter parser.

Key features:
- Automatically replaces Chinese colons (：) with English colons (:) in frontmatter
- Graceful degradation when YAML is malformed
- Separates frontmatter metadata from body content
"""

import os
import shutil
import re
import yaml
from typing import Tuple, Dict, Any, Optional
from scripts.encoding_utils import safe_open, ensure_nfc


# Regex to match YAML frontmatter delimited by ---
_FRONTMATTER_RE = re.compile(
    r'^---[ \t]*\r?\n(.*?)^---[ \t]*\r?\n',
    re.DOTALL | re.MULTILINE
)


def _replace_chinese_colons(fm_text: str) -> str:
    """Replace Chinese full-width colons with English colons in the frontmatter area only."""
    return fm_text.replace('：', ': ')


def _clean_frontmatter(fm_text: str) -> str:
    """Apply all pre-processing fixes to frontmatter text before YAML parsing."""
    fm_text = _replace_chinese_colons(fm_text)
    # Remove trailing whitespace on each line (but preserve indentation)
    fm_text = '\n'.join(line.rstrip() for line in fm_text.split('\n'))
    return fm_text


def parse_frontmatter(filepath: str) -> Tuple[Dict[str, Any], str]:
    """
    Parse a Markdown file, separating frontmatter (YAML) from body.

    Args:
        filepath: Path to the .md file (supports Chinese paths).

    Returns:
        Tuple of (frontmatter_dict, body_text).
        frontmatter_dict is empty if no valid frontmatter is found.
    """
    with safe_open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    return parse_frontmatter_string(content)


def parse_frontmatter_string(content: str) -> Tuple[Dict[str, Any], str]:
    """
    Parse frontmatter from a string of Markdown content.

    Args:
        content: Raw Markdown string.

    Returns:
        Tuple of (frontmatter_dict, body_text).
    """
    match = _FRONTMATTER_RE.match(content)

    if not match:
        # No frontmatter delimiters found; entire content is body
        return {}, content

    fm_text = match.group(1)
    body = content[match.end():]

    # Apply high-tolerance preprocessing
    fm_text = _clean_frontmatter(fm_text)

    try:
        fm_dict = yaml.safe_load(fm_text)
        if fm_dict is None:
            fm_dict = {}
        if not isinstance(fm_dict, dict):
            # YAML parsed but returned a scalar/list instead of dict
            fm_dict = {}
    except yaml.YAMLError as e:
        # Malformed YAML — degrade gracefully
        print(f"[frontmatter_parser] YAML parse warning: {e}")
        fm_dict = {}

    return fm_dict, body


def get_frontmatter_field(filepath: str, field: str) -> Optional[Any]:
    """Read a single field from a file's frontmatter without parsing the body."""
    fm, _ = parse_frontmatter(filepath)
    return fm.get(field)


def has_frontmatter(content: str) -> bool:
    """Check if content string begins with YAML frontmatter delimiters."""
    return content.startswith('---\n') or content.startswith('---\r\n')


def extract_user_area(body: str) -> Optional[str]:
    """
    Extract content between <!-- USER_AREA_START --> and <!-- USER_AREA_END --> markers.

    Returns None if markers are not found.
    """
    pattern = r'<!-- USER_AREA_START -->\s*\n(.*?)\n\s*<!-- USER_AREA_END -->'
    match = re.search(pattern, body, re.DOTALL)
    if match:
        return match.group(1)
    return None


def preserve_user_area(original_body: str, new_body: str) -> str:
    """
    When updating a file body, ensure the user area content is preserved.
    Takes the user area from original_body and injects it into new_body.
    """
    original_user = extract_user_area(original_body)
    new_user = extract_user_area(new_body)

    if original_user is None:
        return new_body

    if new_user is None:
        return new_body

    # Replace the user area in new_body with the one from original_body
    return new_body.replace(new_user, original_user)


# ─── File I/O helpers (migrated from state_updater) ──────────

def backup_file(filepath: str) -> Optional[str]:
    """Create a .bak backup of a file. Returns backup path or None."""
    filepath = ensure_nfc(filepath)
    if not os.path.isfile(filepath):
        return None
    backup_path = ensure_nfc(filepath + '.bak')
    shutil.copy2(filepath, backup_path)
    return backup_path


def write_md_with_frontmatter(
    filepath: str, fm: Dict[str, Any], body: str, backup: bool = True
) -> None:
    """
    Write a Markdown file with YAML frontmatter and body. Optionally creates .bak first.

    Args:
        filepath: Absolute path to the .md file.
        fm: Dict of frontmatter key-value pairs.
        body: Markdown body text (must be a string).
        backup: If True (default), create a .bak before overwriting.
    """
    if not isinstance(body, str):
        raise TypeError(f'body must be str, got {type(body).__name__}')

    if backup:
        backup_file(filepath)

    fm_text = yaml.safe_dump(
        fm,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
    ).strip()
    content = f'---\n{fm_text}\n---\n\n{body}'

    with safe_open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
