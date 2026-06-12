"""write-novel data modules — lightweight adapters for Markdown-First architecture.

All modules read from Markdown source files (the truth) or .write-novel/
projected JSON (rebuildable cache). No SQLite, no external databases.
"""

from scripts.data_modules.config import DataModulesConfig
from scripts.data_modules.state_manager import StateManager
from scripts.data_modules.context_manager import ContextManager
from scripts.data_modules.chapter_commit import ChapterCommitService

__all__ = [
    "DataModulesConfig",
    "StateManager",
    "ContextManager",
    "ChapterCommitService",
]
