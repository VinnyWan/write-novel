import json
import os
from typing import Any, Dict, List

from scripts.encoding_utils import ensure_nfc


REQUIRED_PLUGIN_FIELDS = ["name", "version", "description", "keywords", "compatibility", "commands", "skills", "agents", "files"]


def load_plugin_metadata(project_root: str) -> Dict[str, Any]:
    path = ensure_nfc(os.path.join(project_root, ".claude-plugin", "plugin.json"))
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_plugin_metadata(project_root: str) -> Dict[str, Any]:
    root = ensure_nfc(os.path.abspath(project_root))
    errors: List[str] = []
    warnings: List[str] = []
    try:
        metadata = load_plugin_metadata(root)
    except FileNotFoundError:
        return {"status": "error", "errors": ["缺少 .claude-plugin/plugin.json"], "warnings": []}
    except json.JSONDecodeError as exc:
        return {"status": "error", "errors": [f".claude-plugin/plugin.json 不是有效 JSON：{exc}"], "warnings": []}

    if not isinstance(metadata, dict):
        return {"status": "error", "errors": [".claude-plugin/plugin.json 顶层必须是对象"], "warnings": []}

    for field in REQUIRED_PLUGIN_FIELDS:
        if field not in metadata or metadata[field] in (None, "", []):
            errors.append(f"缺少必需字段：{field}")

    for list_field in ["commands", "skills", "agents", "files", "keywords"]:
        if list_field in metadata and not isinstance(metadata[list_field], list):
            errors.append(f"{list_field} 必须是数组")

    for field in ["skills", "agents", "files"]:
        values = metadata.get(field, [])
        if not isinstance(values, list):
            continue
        for rel in values:
            if not isinstance(rel, str):
                errors.append(f"{field} 包含非字符串路径")
                continue
            path = ensure_nfc(os.path.join(root, rel))
            if not os.path.isfile(path):
                errors.append(f"{field} 引用不存在：{rel}")

    commands = metadata.get("commands", [])
    if isinstance(commands, list):
        for command in commands:
            if not isinstance(command, str) or not command.strip():
                errors.append("commands 包含无效命令")
        main_path = os.path.join(root, "scripts", "main.py")
        if os.path.isfile(main_path):
            with open(main_path, "r", encoding="utf-8") as f:
                main_text = f.read()
            import re
            exposed = set(re.findall(r"subparsers\.add_parser\('([^']+)'", main_text))
            missing = sorted(exposed - set(commands))
            for command in missing:
                errors.append(f"commands 缺少 CLI 子命令：{command}")

    readme = os.path.join(root, "README.md")
    if os.path.isfile(readme):
        with open(readme, "r", encoding="utf-8") as f:
            readme_text = f.read()
        for command in metadata.get("commands", []):
            if command not in readme_text:
                warnings.append(f"README 可能缺少命令说明：{command}")
    else:
        warnings.append("缺少 README.md")

    status = "error" if errors else "warning" if warnings else "ok"
    return {"status": status, "errors": errors, "warnings": warnings}


def format_validation_text(result: Dict[str, Any]) -> str:
    lines = [f"插件校验状态：{result['status']}"]
    for error in result.get("errors", []):
        lines.append(f"[error] {error}")
    for warning in result.get("warnings", []):
        lines.append(f"[warning] {warning}")
    if len(lines) == 1:
        lines.append("所有插件元数据检查通过。")
    return "\n".join(lines)
