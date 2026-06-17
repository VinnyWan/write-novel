#!/usr/bin/env python3
"""Scan markdown files for banned words/patterns."""
import argparse
import json
import re
import sys
from pathlib import Path

# 5-star banned words (must replace)
STAR5_PATTERNS = [
    r'命运的齿轮',
    r'心猛地一沉',
    r'眼神复杂',
    r'深刻变化',
    r'踏上新的旅程',
    r'这一切都说明',
    r'他终于明白',
    r'新的篇章',
    r'不可否认的是',
    r'与此同时',
]

# 4-star banned words (should replace)
STAR4_PATTERNS = [
    r'一股?莫名的',
    r'不知?不觉',
    r'深不见底',
    r'电光火石',
]

# Banned sentence patterns
BANNED_SENTENCE_PATTERNS = [
    (r'不是[^，。；,!]{1,20}而是', '不是A而是B句式'),
    (r'却不知[^，。；,!]{1,30}', '却不知...句式'),
    (r'或许[^，。；,!]{1,10}或许', '或许...或许句式'),
]


def scan_file(filepath: Path) -> dict:
    text = filepath.read_text(encoding='utf-8')
    lines = text.split('\n')
    findings = []

    for i, line in enumerate(lines, 1):
        for pat in STAR5_PATTERNS:
            for m in re.finditer(pat, line):
                findings.append({
                    "line": i,
                    "level": "5-star",
                    "pattern": pat,
                    "match": m.group(),
                    "context": line.strip()[:80],
                })
        for pat in STAR4_PATTERNS:
            for m in re.finditer(pat, line):
                findings.append({
                    "line": i,
                    "level": "4-star",
                    "pattern": pat,
                    "match": m.group(),
                    "context": line.strip()[:80],
                })
        for pat, name in BANNED_SENTENCE_PATTERNS:
            for m in re.finditer(pat, line):
                findings.append({
                    "line": i,
                    "level": "pattern",
                    "pattern": name,
                    "match": m.group(),
                    "context": line.strip()[:80],
                })

    return {
        "file": str(filepath),
        "total_findings": len(findings),
        "star5_count": sum(1 for f in findings if f["level"] == "5-star"),
        "star4_count": sum(1 for f in findings if f["level"] == "4-star"),
        "pattern_count": sum(1 for f in findings if f["level"] == "pattern"),
        "findings": findings,
    }


def main():
    parser = argparse.ArgumentParser(description="Scan for banned words in markdown")
    parser.add_argument("--file", required=True, help="Path to markdown file")
    args = parser.parse_args()

    fp = Path(args.file)
    if not fp.exists():
        print(json.dumps({"error": f"File not found: {args.file}"}))
        sys.exit(1)

    result = scan_file(fp)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
