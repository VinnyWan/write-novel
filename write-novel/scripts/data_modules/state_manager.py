"""State manager — reads/writes .write-novel/state.json projected from Markdown."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from scripts.data_modules.config import DataModulesConfig
from scripts.encoding_utils import ensure_nfc, safe_open
from scripts.frontmatter_parser import parse_frontmatter


class StateManager:
    """Reads project state from Markdown files (truth) and .write-novel/ cache."""

    def __init__(self, config: DataModulesConfig):
        self.config = config

    def read_global_state(self) -> Dict[str, Any]:
        """Read 全局写作状态.md frontmatter as the authoritative state."""
        state_path = ensure_nfc(str(self.config.project_root / "全局写作状态.md"))
        if not os.path.isfile(state_path):
            return {}
        fm, body = parse_frontmatter(state_path)
        fm["_body"] = body
        return fm

    def read_cached_state(self) -> Dict[str, Any]:
        """Read .write-novel/state.json cache (may be stale)."""
        cache_path = self.config.state_file
        if not cache_path.is_file():
            return {}
        with safe_open(str(cache_path), "r", encoding="utf-8") as f:
            return json.load(f)

    def write_cached_state(self, data: Dict[str, Any]) -> None:
        """Write .write-novel/state.json cache."""
        self.config.write_novel_dir.mkdir(parents=True, exist_ok=True)
        cache_path = str(self.config.state_file)
        with safe_open(cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_character_list(self) -> list[Dict[str, Any]]:
        """List all characters from 人物/ directory frontmatters."""
        chars = []
        char_dir = self.config.characters_dir
        if not char_dir.is_dir():
            return chars
        for f in sorted(char_dir.glob("*.md")):
            fm, _ = parse_frontmatter(str(f))
            if fm:
                fm["_file"] = f.name
                chars.append(fm)
        return chars

    def get_chapter_list(self) -> list[Dict[str, Any]]:
        """List all chapter drafts from 章节草稿/ directory."""
        chapters = []
        draft_dir = self.config.drafts_dir
        if not draft_dir.is_dir():
            return chapters
        for f in sorted(draft_dir.glob("*.md")):
            fm, body = parse_frontmatter(str(f))
            chapters.append({
                "file": f.name,
                "size": len(body) if body else 0,
                "frontmatter": fm,
            })
        return chapters

    def get_summary_list(self) -> list[Dict[str, Any]]:
        """List all chapter summaries from 历史章节摘要/ directory."""
        summaries = []
        summary_dir = self.config.summaries_dir
        if not summary_dir.is_dir():
            return summaries
        for f in sorted(summary_dir.glob("*.md")):
            with safe_open(str(f), "r", encoding="utf-8") as fh:
                content = fh.read()
            summaries.append({
                "file": f.name,
                "content": content[:300],
            })
        return summaries

    def get_progress_snapshot(self) -> Dict[str, Any]:
        """Compute current progress snapshot."""
        state = self.read_global_state()
        chapters = self.get_chapter_list()
        summaries = self.get_summary_list()
        total_words = sum(ch.get("size", 0) for ch in chapters)
        return {
            "current_volume": state.get("当前分卷", state.get("当前卷", "")),
            "current_chapter": state.get("当前章节", ""),
            "protagonist": state.get("主角姓名", ""),
            "completed_chapters": state.get("已完成章数", len(chapters)),
            "completed_words": state.get("已完成字数", total_words),
            "chapter_files": len(chapters),
            "summary_files": len(summaries),
            "last_updated": state.get("最后更新时间", ""),
        }
