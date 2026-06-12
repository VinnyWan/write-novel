"""Chapter commit service — record chapter completion and update state."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from scripts.data_modules.config import DataModulesConfig
from scripts.frontmatter_parser import parse_frontmatter, write_md_with_frontmatter


@dataclass
class ChapterCommitResult:
    """Result of a chapter commit operation."""
    chapter: int
    title: str
    word_count: int
    new_characters: List[str] = field(default_factory=list)
    new_settings: List[str] = field(default_factory=list)
    new_foreshadowing: List[str] = field(default_factory=list)
    resolved_foreshadowing: List[str] = field(default_factory=list)


class ChapterCommitService:
    """Handles chapter commit: archive, summarize, update state, track foreshadowing."""

    def __init__(self, config: DataModulesConfig):
        self.config = config

    def commit_chapter(
        self,
        chapter_num: int,
        title: str,
        body: str,
        new_characters: Optional[List[str]] = None,
        new_settings: Optional[List[str]] = None,
        new_plots: Optional[List[str]] = None,
        resolved_plots: Optional[List[str]] = None,
    ) -> ChapterCommitResult:
        """Commit a completed chapter: save draft, generate summary, update state."""
        # Save draft
        draft_path = self.config.drafts_dir / f"第{chapter_num}章_{title}.md"
        draft_path.parent.mkdir(parents=True, exist_ok=True)
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        frontmatter = {
            "章节序号": chapter_num,
            "标题": title,
            "提交时间": now,
            "字数": len(body),
        }
        write_md_with_frontmatter(str(draft_path), frontmatter, body)

        # Generate summary (~200 chars)
        summary = body[:200].replace("\n", " ") + ("..." if len(body) > 200 else "")
        summary_path = self.config.summaries_dir / f"第{chapter_num}章_摘要.md"
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        write_md_with_frontmatter(
            str(summary_path),
            {"章节序号": chapter_num, "标题": title, "字数": len(body)},
            summary,
        )

        # Record commit
        commit_dir = self.config.project_root / "章节提交记录"
        commit_dir.mkdir(parents=True, exist_ok=True)
        commit_path = commit_dir / f"第{chapter_num}章_提交记录.md"
        record = f"## 第{chapter_num}章提交记录\n\n"
        record += f"- 提交时间: {now}\n- 标题: {title}\n- 字数: {len(body)}\n\n"
        if new_characters:
            record += "### 新增角色\n" + "\n".join(f"- {c}" for c in new_characters) + "\n\n"
        if new_settings:
            record += "### 新增设定\n" + "\n".join(f"- {s}" for s in new_settings) + "\n\n"
        if new_plots:
            record += "### 新增伏笔\n" + "\n".join(f"- {p}" for p in new_plots) + "\n\n"
        if resolved_plots:
            record += "### 回收伏笔\n" + "\n".join(f"- {p}" for p in resolved_plots) + "\n\n"
        commit_path.write_text(record, encoding="utf-8")

        return ChapterCommitResult(
            chapter=chapter_num,
            title=title,
            word_count=len(body),
            new_characters=new_characters or [],
            new_settings=new_settings or [],
            new_foreshadowing=new_plots or [],
            resolved_foreshadowing=resolved_plots or [],
        )
