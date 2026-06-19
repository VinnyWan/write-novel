#!/usr/bin/env python3
"""write-novel behavior eval runner.

Reads evals/fixtures/behavior/fast.json and executes each case as a
structural/grep assertion, printing pass/fail. Exit 0 on all green, 1 on any
failure. Python is used here as a deterministic data-processing tool (JSON
parse + dispatch), permitted by CLAUDE.md for "编码处理等底层确定性工具".
"""
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional


def plugin_root() -> Path:
    return Path(sys.argv[1])


def grep_in_files(needle: str, files) -> bool:
    """True if needle appears in any of the given file paths (recursively for dirs)."""
    args = ["grep", "-rq", "--", needle]
    args.extend(str(f) for f in files)
    try:
        subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False


def first_line_no(needle: str, files) -> Optional[int]:
    """First line number where needle appears across files, or None."""
    args = ["grep", "-rn", "--", needle]
    args.extend(str(f) for f in files)
    try:
        out = subprocess.run(args, capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError:
        return None
    for line in out.splitlines():
        # format: path:lineno:content
        parts = line.split(":", 2)
        if len(parts) >= 2 and parts[1].isdigit():
            return int(parts[1])
    return None


def case_skill_frontmatter(case, root: Path) -> tuple[bool, str]:
    missing = []
    for skill_dir in sorted((root / "skills").iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            missing.append(f"missing SKILL.md in {skill_dir.name}")
            continue
        text = skill_md.read_text(encoding="utf-8", errors="replace")
        if not text.startswith("---"):
            missing.append(f"{skill_dir.name}: no frontmatter")
            continue
        fm = text.split("---", 2)[1] if text.count("---") >= 2 else ""
        if "\nname:" not in "\n" + fm and not fm.startswith("name:"):
            missing.append(f"{skill_dir.name}: missing name")
        if "\ndescription:" not in "\n" + fm and not fm.startswith("description:"):
            missing.append(f"{skill_dir.name}: missing description")
    if missing:
        return False, "; ".join(missing)
    return True, ""


def case_skill_contract(case, root: Path) -> tuple[bool, str]:
    skill = case["skill"]
    skill_dir = root / "skills" / skill
    if not skill_dir.is_dir():
        return False, f"skill dir not found: {skill}"
    search_files = [skill_dir / "SKILL.md"]
    refs = skill_dir / "references"
    if refs.is_dir():
        search_files.append(refs)
    missing = [p for p in case["required"] if not grep_in_files(p, search_files)]
    if missing:
        return False, f"missing phrases: {missing}"
    return True, ""


def case_ordered_phrases(case, root: Path) -> tuple[bool, str]:
    skill = case["skill"]
    skill_md = root / "skills" / skill / "SKILL.md"
    if not skill_md.is_file():
        return False, f"SKILL.md not found for {skill}"
    # ordered checks apply to the SKILL.md flow narrative only (not references),
    # because the same phrase may appear earlier in a reference file and skew line order.
    search_files = [skill_md]
    for pair in case["ordered"]:
        first, second = pair
        f_line = first_line_no(first, search_files)
        s_line = first_line_no(second, search_files)
        if f_line is None or s_line is None:
            return False, f"phrase not found in SKILL.md ({first!r}={f_line}, {second!r}={s_line})"
        if f_line >= s_line:
            return False, f"order violated: '{first}' line {f_line} >= '{second}' line {s_line}"
    return True, ""


def case_reference_exists(case, root: Path) -> tuple[bool, str]:
    return case_files_exist(case, root)


def case_file_exists(case, root: Path) -> tuple[bool, str]:
    return case_files_exist(case, root)


def case_files_exist(case, root: Path) -> tuple[bool, str]:
    missing = [f for f in case["required_files"] if not (root / f).is_file()]
    if missing:
        return False, f"missing: {missing}"
    return True, ""


def case_artifact_schema(case, root: Path) -> tuple[bool, str]:
    schema = root / case["schema_file"]
    if not schema.is_file():
        return False, f"schema file not found: {case['schema_file']}"
    text = schema.read_text(encoding="utf-8", errors="replace")
    missing = [fld for fld in case["required_fields"] if fld not in text]
    if missing:
        return False, f"missing fields: {missing}"
    return True, ""


def case_error_catalog(case, root: Path) -> tuple[bool, str]:
    catalog = root / case["catalog_file"]
    if not catalog.is_file():
        return False, f"catalog not found: {case['catalog_file']}"
    try:
        data = json.loads(catalog.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, f"invalid JSON: {e}"
    codes = {e.get("code") for e in data.get("errors", [])}
    missing = [c for c in case["required_codes"] if c not in codes]
    if missing:
        return False, f"missing codes: {missing}"
    return True, ""


def case_glossary(case, root: Path) -> tuple[bool, str]:
    glossary = root / case["glossary_file"]
    if not glossary.is_file():
        return False, f"glossary not found: {case['glossary_file']}"
    try:
        data = json.loads(glossary.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, f"invalid JSON: {e}"
    terms = {t.get("technical") for t in data.get("terms", [])}
    missing = [t for t in case["required_terms"] if t not in terms]
    if missing:
        return False, f"missing terms: {missing}"
    return True, ""


def case_shared_file_contract(case, root: Path) -> tuple[bool, str]:
    f = root / case["file"]
    if not f.is_file():
        return False, f"file not found: {case['file']}"
    text = f.read_text(encoding="utf-8", errors="replace")
    missing = [p for p in case["required"] if p not in text]
    if missing:
        return False, f"missing phrases in {case['file']}: {missing}"
    return True, ""


def case_delegated_check(case, root: Path) -> tuple[bool, str]:
    script = root / case["delegate"]
    if not script.is_file():
        return False, f"delegate script not found: {case['delegate']}"
    try:
        subprocess.run(["bash", str(script)], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        tail = "\n".join((e.stderr or e.stdout or "").splitlines()[-5:])
        return False, f"{script.name} exit {e.returncode}: {tail}"
    return True, ""


DISPATCH = {
    "skill_frontmatter": case_skill_frontmatter,
    "skill_contract": case_skill_contract,
    "ordered_phrases": case_ordered_phrases,
    "reference_exists": case_reference_exists,
    "file_exists": case_file_exists,
    "artifact_schema": case_artifact_schema,
    "error_catalog": case_error_catalog,
    "glossary": case_glossary,
    "shared_file_contract": case_shared_file_contract,
    "delegated_check": case_delegated_check,
}

GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"


def main() -> int:
    root = plugin_root()
    eval_file = root / "evals" / "fixtures" / "behavior" / "fast.json"
    if not eval_file.is_file():
        print(f"Error: eval fixture not found: {eval_file}", file=sys.stderr)
        return 2
    data = json.loads(eval_file.read_text(encoding="utf-8"))
    cases = data["cases"]

    passed = 0
    failed = []
    print(f"\n=== Behavior Evals ({len(cases)} cases) ===")
    for case in cases:
        ctype = case["type"]
        handler = DISPATCH.get(ctype)
        if handler is None:
            print(f"  [{RED}FAIL{RESET}] {case['id']} — unknown type: {ctype}")
            failed.append(case["id"])
            continue
        try:
            ok, detail = handler(case, root)
        except Exception as e:  # noqa: BLE001
            ok, detail = False, f"exception: {e}"
        if ok:
            print(f"  [{GREEN}PASS{RESET}] {case['id']}")
            passed += 1
        else:
            print(f"  [{RED}FAIL{RESET}] {case['id']}" + (f" — {detail}" if detail else ""))
            failed.append(case["id"])

    print(f"\nTotal: {len(cases)} | Pass: {passed} | Fail: {len(failed)}")
    if failed:
        print(f"Failed: {failed}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
