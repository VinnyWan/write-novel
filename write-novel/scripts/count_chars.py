#!/usr/bin/env python3
"""Count Chinese characters in markdown files."""
import argparse
import json
import re
import sys
from pathlib import Path


def count_chinese_chars(text: str) -> int:
    return len(re.findall(r'[一-鿿㐀-䶿]', text))


def count_stats(filepath: Path) -> dict:
    text = filepath.read_text(encoding='utf-8')
    lines = text.split('\n')
    paragraphs = [l for l in lines if l.strip() and not l.strip().startswith('#')]
    chinese_chars = count_chinese_chars(text)
    return {
        "file": str(filepath),
        "chinese_chars": chinese_chars,
        "total_chars": len(text),
        "paragraphs": len(paragraphs),
        "lines": len(lines),
    }


def main():
    parser = argparse.ArgumentParser(description="Count Chinese characters in markdown")
    parser.add_argument("--file", required=True, help="Path to markdown file")
    parser.add_argument("--json", action="store_true", default=True, help="Output as JSON")
    args = parser.parse_args()

    fp = Path(args.file)
    if not fp.exists():
        print(json.dumps({"error": f"File not found: {args.file}"}))
        sys.exit(1)

    stats = count_stats(fp)
    print(json.dumps(stats, ensure_ascii=False))


if __name__ == "__main__":
    main()
