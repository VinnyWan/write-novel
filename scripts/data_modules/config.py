"""Project configuration adapter for write-novel."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class DataModulesConfig:
    """Configuration sourced from project Markdown files and .write-novel/ cache."""

    project_root: Path
    write_novel_dir: Path = field(init=False)
    state_file: Path = field(init=False)
    search_index_file: Path = field(init=False)

    # Directories (relative to project_root)
    characters_dir: Path = field(init=False)
    world_settings_dir: Path = field(init=False)
    outlines_dir: Path = field(init=False)
    drafts_dir: Path = field(init=False)
    summaries_dir: Path = field(init=False)

    def __post_init__(self):
        self.project_root = Path(self.project_root).resolve()
        self.write_novel_dir = self.project_root / ".write-novel"
        self.state_file = self.write_novel_dir / "state.json"
        self.search_index_file = self.write_novel_dir / "search_index.json"

        self.characters_dir = self.project_root / "人物"
        self.world_settings_dir = self.project_root / "世界设定"
        self.outlines_dir = self.project_root / "分卷大纲"
        self.drafts_dir = self.project_root / "章节草稿"
        self.summaries_dir = self.project_root / "历史章节摘要"

    @classmethod
    def from_project_root(cls, project_root: str | Path) -> "DataModulesConfig":
        return cls(project_root=Path(project_root))

    def ensure_dirs(self) -> list[Path]:
        """Ensure all project directories exist, return list of created dirs."""
        created = []
        for d in [
            self.characters_dir,
            self.world_settings_dir,
            self.outlines_dir,
            self.drafts_dir,
            self.summaries_dir,
            self.write_novel_dir,
        ]:
            if not d.exists():
                d.mkdir(parents=True, exist_ok=True)
                created.append(d)
        return created
