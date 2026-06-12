"""Path traversal guard -- ensure all file reads stay within project root."""
from pathlib import Path


def safe_resolve(project_root: Path, relative_path: str) -> Path:
    """Resolve a relative path within project_root, preventing traversal."""
    root = project_root.resolve()
    target = (root / relative_path).resolve()
    target.relative_to(root)  # raises ValueError if escapes
    return target
