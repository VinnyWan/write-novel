#!/usr/bin/env python3
"""Extract structured metadata from project files for Dashboard consumption."""
import argparse
import json
import re
import sys
from pathlib import Path


def extract_chapter_meta(filepath: Path) -> dict:
    text = filepath.read_text(encoding='utf-8')
    chinese_chars = len(re.findall(r'[一-鿿㐀-䶿]', text))
    # Extract chapter title from first heading
    title = ""
    m = re.search(r'^#\s+(.*)', text, re.MULTILINE)
    if m:
        title = m.group(1).strip()
    # Extract chapter number from filename
    num = re.search(r'第0*(\d+)章', str(filepath))
    chapter_num = int(num.group(1)) if num else 0

    return {
        "file": str(filepath),
        "chapter_number": chapter_num,
        "title": title,
        "chinese_chars": chinese_chars,
    }


def extract_character_meta(filepath: Path) -> dict:
    text = filepath.read_text(encoding='utf-8')
    m = re.search(r'^---\s*\n(.*?)\n---', text, re.DOTALL)
    fm = {}
    if m:
        for line in m.group(1).split('\n'):
            kv = re.match(r'^(\w[\w_-]*)\s*:\s*(.*)', line)
            if kv:
                fm[kv.group(1)] = kv.group(2).strip()
    name = fm.get('name', filepath.stem)
    return {"file": str(filepath), "name": name, "role": fm.get('role', 'unknown')}


def main():
    parser = argparse.ArgumentParser(description="Extract metadata from project files")
    parser.add_argument("--project-root", required=True, help="Project root directory")
    parser.add_argument("--type", choices=["chapters", "characters", "all"], default="all")
    args = parser.parse_args()

    root = Path(args.project_root)
    result = {"chapters": [], "characters": []}

    # Find chapters
    for pattern in ["正文/第*章*.md", "正文/Chapter-*.md"]:
        for p in root.glob(pattern):
            result["chapters"].append(extract_chapter_meta(p))

    # Find characters
    char_dir = root / "设定" / "角色"
    if char_dir.exists():
        for p in char_dir.glob("*.md"):
            result["characters"].append(extract_character_meta(p))

    # Sort chapters by number
    result["chapters"].sort(key=lambda x: x["chapter_number"])
    result["chapter_count"] = len(result["chapters"])
    result["character_count"] = len(result["characters"])
    result["total_chinese_chars"] = sum(c["chinese_chars"] for c in result["chapters"])

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
