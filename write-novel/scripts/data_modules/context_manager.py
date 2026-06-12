"""Context manager — assembles writing context for a target chapter."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from scripts.data_modules.config import DataModulesConfig
from scripts.encoding_utils import ensure_nfc
from scripts.frontmatter_parser import parse_frontmatter


class ContextManager:
    """Assembles writing context: characters, settings, foreshadowing, summaries."""

    def __init__(self, config: DataModulesConfig):
        self.config = config

    def gather_context(self, volume: int, chapter: int) -> Dict[str, Any]:
        """Gather all relevant context for writing a specific chapter.

        Returns a dict with keys: characters, settings, foreshadowing,
        previous_summary, outline, constraints.
        """
        context = {
            "characters": self._load_characters(),
            "settings": self._load_settings(),
            "foreshadowing": self._load_foreshadowing(),
            "previous_summary": self._load_previous_summary(chapter),
            "outline": self._load_outline(volume, chapter),
            "constraints": self._load_constraints(),
        }
        return context

    def _load_characters(self) -> List[Dict[str, Any]]:
        chars = []
        char_dir = self.config.characters_dir
        if not char_dir.is_dir():
            return chars
        for f in sorted(char_dir.glob("*.md")):
            fm, body = parse_frontmatter(str(f))
            if fm:
                chars.append({
                    "name": fm.get("姓名", f.stem),
                    "realm": fm.get("当前境界", ""),
                    "status": fm.get("当前状态", ""),
                    "location": fm.get("当前位置", ""),
                    "goal": fm.get("长线剧情目标", ""),
                    "file": f.name,
                })
        return chars

    def _load_settings(self) -> List[Dict[str, Any]]:
        settings = []
        ws_dir = self.config.world_settings_dir
        if not ws_dir.is_dir():
            return settings
        for f in sorted(ws_dir.glob("*.md")):
            fm, body = parse_frontmatter(str(f))
            settings.append({
                "file": f.name,
                "frontmatter": fm,
                "has_body": bool(body and body.strip()),
            })
        return settings

    def _load_foreshadowing(self) -> Dict[str, Any]:
        fp = self.config.project_root / "伏笔与线索回收池.md"
        if not fp.is_file():
            return {"items": [], "summary": {"total": 0, "buried": 0, "developing": 0, "resolved": 0}}
        with open(str(fp), "r", encoding="utf-8") as f:
            content = f.read()
        items = self._parse_foreshadow_table(content)
        summary = {
            "total": len(items),
            "buried": sum(1 for i in items if "🟡" in i.get("status", "")),
            "developing": sum(1 for i in items if "🟠" in i.get("status", "")),
            "resolved": sum(1 for i in items if "🟢" in i.get("status", "")),
        }
        return {"items": items, "summary": summary}

    def _parse_foreshadow_table(self, content: str) -> List[Dict[str, str]]:
        """Parse a Markdown table of foreshadowing items."""
        items = []
        lines = content.split("\n")
        header_found = False
        for line in lines:
            line = line.strip()
            if not line.startswith("|"):
                continue
            if not header_found:
                header_found = True
                continue
            if line.startswith("|---") or line.startswith("| --"):
                continue
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if len(cells) >= 4:
                items.append({
                    "id": cells[0] if len(cells) > 0 else "",
                    "content": cells[1] if len(cells) > 1 else "",
                    "status": cells[2] if len(cells) > 2 else "",
                    "target_chapter": cells[3] if len(cells) > 3 else "",
                })
        return items

    def _load_previous_summary(self, chapter: int) -> Optional[str]:
        if chapter <= 1:
            return None
        prev = self.config.summaries_dir / f"第{chapter - 1}章_摘要.md"
        if prev.is_file():
            with open(str(prev), "r", encoding="utf-8") as f:
                return f.read()[:500]
        return None

    def _load_outline(self, volume: int, chapter: int) -> Optional[Dict[str, Any]]:
        outline_dir = self.config.outlines_dir
        for pattern in [
            f"第{volume}卷_细纲_第{chapter}章.md",
            f"第{volume}卷_大纲_第{chapter}章.md",
        ]:
            fp = outline_dir / pattern
            if fp.is_file():
                fm, body = parse_frontmatter(str(fp))
                return {"file": fp.name, "frontmatter": fm, "body": body}
        return None

    def _load_constraints(self) -> Dict[str, Any]:
        state_path = self.config.project_root / "全局写作状态.md"
        if not state_path.is_file():
            return {}
        fm, body = parse_frontmatter(str(state_path))
        return {
            "style_notes": fm.get("写作风格", ""),
            "banned_words": fm.get("高压线禁用词", ""),
            "target_platform": fm.get("目标平台", "起点"),
        }
