#!/usr/bin/env python3
"""Generate machine-readable project status snapshot."""
import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def count_chinese(text: str) -> int:
    return len(re.findall(r'[一-鿿㐀-䶿]', text))


def scan_book(book_dir: Path) -> dict:
    chapters = []
    prose_dir = book_dir / "正文"
    if prose_dir.exists():
        for f in sorted(prose_dir.glob("*.md")):
            text = f.read_text(encoding='utf-8')
            chapters.append({
                "file": str(f.relative_to(book_dir)),
                "chinese_chars": count_chinese(text),
            })

    # Count foreshadowing
    fsp_file = book_dir / "追踪" / "伏笔.md"
    fsp = {"total": 0, "buried": 0, "resolved": 0}
    if fsp_file.exists():
        text = fsp_file.read_text(encoding='utf-8')
        fsp["total"] = text.count('\n|')
        fsp["buried"] = text.count('已埋')
        fsp["resolved"] = text.count('已回收')

    # Check outline count
    outline_dir = book_dir / "大纲"
    outline_count = 0
    if outline_dir.exists():
        outline_count = len(list(outline_dir.glob("细纲_第*.md")))

    return {
        "book_name": book_dir.name,
        "chapter_count": len(chapters),
        "outline_count": outline_count,
        "total_chinese_chars": sum(c["chinese_chars"] for c in chapters),
        "foreshadowing": fsp,
        "chapters": chapters,
    }


def main():
    parser = argparse.ArgumentParser(description="Generate project status snapshot")
    parser.add_argument("--project-root", required=True, help="Project root directory")
    parser.add_argument("--output", help="Output path for JSON (default: stdout)")
    args = parser.parse_args()

    root = Path(args.project_root)
    books = []

    # Discover books: find 追踪/ directories
    for fsp_dir in root.glob("*/追踪"):
        book_dir = fsp_dir.parent
        if book_dir.name not in ("拆文库", "对标", "demo"):
            books.append(scan_book(book_dir))

    # Check for short story (正文.md at top level or one level deep)
    for pattern in ["*/正文.md", "短篇/*/正文.md"]:
        for prose_file in root.glob(pattern):
            text = prose_file.read_text(encoding='utf-8')
            books.append({
                "book_name": prose_file.parent.name if prose_file.parent != root else root.name,
                "type": "short",
                "chapter_count": 1,
                "total_chinese_chars": count_chinese(text),
            })

    status = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "project_root": str(root),
        "book_count": len(books),
        "books": books,
    }

    output = json.dumps(status, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
    else:
        print(output)


if __name__ == "__main__":
    main()
