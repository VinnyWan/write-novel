import json
import os
from html import escape
from typing import Any, Dict, List, Optional

from scripts.encoding_utils import ensure_nfc


REQUIRED_REFERENCE_FIELDS = ["id", "category", "genre_tags", "source_note", "applicability", "content"]
DEFAULT_REFERENCE_FILE = os.path.join("references", "writing_references.json")


def reference_file_path(project_root: str, reference_file: Optional[str] = None) -> str:
    if reference_file:
        return ensure_nfc(reference_file if os.path.isabs(reference_file) else os.path.join(project_root, reference_file))
    local = os.path.join(project_root, DEFAULT_REFERENCE_FILE)
    if os.path.isfile(ensure_nfc(local)):
        return ensure_nfc(local)
    package_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return ensure_nfc(os.path.join(package_root, DEFAULT_REFERENCE_FILE))


def validate_reference(item: Dict[str, Any]) -> List[str]:
    errors = []
    for field in REQUIRED_REFERENCE_FIELDS:
        if field not in item or item[field] in (None, "", []):
            errors.append(f"缺少字段：{field}")
    if "genre_tags" in item and not isinstance(item["genre_tags"], list):
        errors.append("genre_tags 必须是列表")
    return errors


def load_references(project_root: str, reference_file: Optional[str] = None) -> List[Dict[str, Any]]:
    path = reference_file_path(project_root, reference_file)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"参考资料 JSON 无效：{path}: {exc}") from exc
    if not isinstance(data, list):
        raise ValueError("参考资料文件必须是 JSON 数组")
    references = []
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"第 {index + 1} 条参考资料不是对象")
        errors = validate_reference(item)
        if errors:
            rid = item.get("id", f"#{index + 1}")
            raise ValueError(f"参考资料 {rid} 无效：{'; '.join(errors)}")
        references.append(item)
    return references


def query_references(
    project_root: str,
    keyword: str = "",
    category: str = "",
    genre: str = "",
    situation: str = "",
    limit: int = 5,
    reference_file: Optional[str] = None,
) -> List[Dict[str, Any]]:
    refs = load_references(project_root, reference_file)
    terms = [term.strip().lower() for term in [keyword, situation] if term.strip()]
    category = category.strip().lower()
    genre = genre.strip().lower()
    scored = []
    for ref in refs:
        haystack = " ".join(
            str(ref.get(key, "")) for key in ["id", "category", "title", "source_note", "applicability", "content"]
        ).lower()
        tag_text = " ".join(str(tag) for tag in ref.get("genre_tags", [])).lower()
        if category and str(ref.get("category", "")).lower() != category:
            continue
        if genre and genre not in tag_text:
            continue
        score = 0
        for term in terms:
            if term and term in haystack:
                score += 2
            if term and term in tag_text:
                score += 1
        if not terms:
            score = 1
        if score > 0:
            scored.append((score, ref))
    scored.sort(key=lambda item: (-item[0], item[1]["id"]))
    return [ref for _, ref in scored[:limit]]


def format_query_results(results: List[Dict[str, Any]]) -> str:
    if not results:
        return "未找到匹配参考资料。"
    lines = []
    for ref in results:
        tags = "、".join(ref.get("genre_tags", []))
        title = ref.get("title") or ref["id"]
        lines.append(f"- [{ref['id']}] {title}（{ref['category']} / {tags}）")
        lines.append(f"  来源：{ref['source_note']}")
        lines.append(f"  适用：{ref['applicability']}")
        lines.append(f"  内容：{ref['content']}")
    return "\n".join(lines)


def build_reference_prompt_context(references: List[Dict[str, Any]], max_chars: int = 800) -> str:
    if not references:
        return "<写作参考资料>无</写作参考资料>"
    parts = ["<写作参考资料>"]
    used = 0
    for ref in references:
        snippet = (
            f"  <参考 id=\"{escape(str(ref['id']), quote=True)}\" "
            f"类别=\"{escape(str(ref['category']), quote=True)}\">"
            f"适用：{escape(str(ref['applicability']))}；"
            f"内容：{escape(str(ref['content']))}</参考>"
        )
        if used + len(snippet) > max_chars:
            break
        parts.append(snippet)
        used += len(snippet)
    parts.append("</写作参考资料>")
    return "\n".join(parts)
