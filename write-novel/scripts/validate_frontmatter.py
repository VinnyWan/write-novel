#!/usr/bin/env python3
"""Validate YAML frontmatter required fields in markdown files."""
import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_FIELDS = {
    "chapter": ["chapter_number", "title"],
    "character": ["name", "role"],
    "setting": [],
}


def detect_doc_type(filepath: Path) -> str:
    path_str = str(filepath).lower()
    if "正文" in path_str or "chapter" in path_str.lower():
        return "chapter"
    if "角色" in path_str or "character" in path_str.lower():
        return "character"
    if "设定" in path_str or "setting" in path_str.lower():
        return "setting"
    return "unknown"


def parse_frontmatter(text: str) -> tuple[dict, str]:
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, re.DOTALL)
    if not m:
        return {}, text
    fm_text = m.group(1)
    body = text[m.end():]
    fm = {}
    for line in fm_text.split('\n'):
        kv = re.match(r'^(\w[\w_-]*)\s*:\s*(.*)', line)
        if kv:
            fm[kv.group(1)] = kv.group(2).strip()
    return fm, body


def validate(filepath: Path) -> dict:
    text = filepath.read_text(encoding='utf-8')
    fm, _ = parse_frontmatter(text)
    doc_type = detect_doc_type(filepath)
    required = REQUIRED_FIELDS.get(doc_type, [])
    missing = [f for f in required if f not in fm or not fm[f]]

    return {
        "file": str(filepath),
        "doc_type": doc_type,
        "has_frontmatter": bool(fm),
        "required_fields": required,
        "missing_fields": missing,
        "valid": len(missing) == 0,
    }


def main():
    parser = argparse.ArgumentParser(description="Validate YAML frontmatter")
    parser.add_argument("--file", required=True, help="Path to markdown file")
    args = parser.parse_args()

    fp = Path(args.file)
    if not fp.exists():
        print(json.dumps({"error": f"File not found: {args.file}"}))
        sys.exit(1)

    result = validate(fp)
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
