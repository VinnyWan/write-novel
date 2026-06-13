#!/usr/bin/env python3
"""De-AI six-gate checker: automated detection for Gates A, B, D.

Usage:
    python deai_check.py <file> [--json] [--intensity light|standard|deep]
    python deai_check.py <file> --json > report.json

Gates:
    A - Banned words/patterns (regex wordlist match)
    B - Sentence pattern templates (regex pattern match)
    D - Rhythm monotonicity (paragraph/sentence length statistics)

Gates C, E, F require Agent semantic judgment and are not automated here.
"""

import argparse
import json
import math
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Optional


# ── Gate A: Banned words ────────────────────────────────────────────

GATE_A_TIER1 = [
    # (pattern, severity, name)
    (re.compile(r"不是.{1,20}而是"), 5, "不是…而是…句式"),
    (re.compile(r"，带着.{1,30}(?:的|之)"), 4, "，带着…万能状语"),
    (re.compile(r"声音不大.{0,10}却带着"), 4, "声音不大却带着…"),
    (re.compile(r"[他她它我你][知道明白清楚懂得].{1,30}[了。]"), 4, "告知式知道/明白"),
    (re.compile(r"(?:仿佛|犹如|宛若).{1,30}一般"), 3, "仿佛…一般"),
    (re.compile(r"眼中闪过.{1,15}(?:的|之|，|。)"), 3, "眼中闪过一丝…"),
    (re.compile(r"嘴角勾起.{1,15}(?:的|笑|，|。)"), 3, "嘴角勾起一抹…"),
    (re.compile(r"心中涌起.{1,15}(?:的|，|。)"), 3, "心中涌起一股…"),
    (re.compile(r"心头一震"), 3, "心头一震"),
]

GATE_A_TIER2 = [
    # (pattern, name, threshold)
    (re.compile(r"眼神复杂"), "眼神复杂", 2),
    (re.compile(r"命运的齿轮"), "命运的齿轮", 1),
    (re.compile(r"心猛地一沉"), "心猛地一沉", 1),
    (re.compile(r"深刻变化"), "深刻变化", 1),
    (re.compile(r"踏上新的旅程"), "踏上新的旅程", 1),
    (re.compile(r"这一切都说明"), "这一切都说明", 1),
    (re.compile(r"他终于明白"), "他终于明白", 1),
    (re.compile(r"新的篇章"), "新的篇章", 1),
    (re.compile(r"与此同时"), "与此同时", 3),
    (re.compile(r"不可否认"), "不可否认", 2),
]

GATE_A_BODY_PARTS = [
    (re.compile(r"身体微微一震"), "身体微微一震"),
    (re.compile(r"瞳孔猛缩"), "瞳孔猛缩"),
    (re.compile(r"呼吸一滞"), "呼吸一滞"),
    (re.compile(r"心跳漏了一拍"), "心跳漏了一拍"),
]

GATE_A_FILLER_ACTIONS = [
    (re.compile(r"沉默了一下"), "沉默了一下"),
    (re.compile(r"顿了顿"), "顿了顿"),
    (re.compile(r"叹了口气"), "叹了口气"),
    (re.compile(r"摇了摇头"), "摇了摇头"),
]


# ── Gate B: Sentence patterns ────────────────────────────────────────

GATE_B_PATTERNS = [
    (re.compile(r"(?:难道|怎么|为什么).{5,30}[？?].{0,50}(?:难道|怎么|为什么).{5,30}[？?]"), "B1", "排比反问≥2"),
    (re.compile(r"^(?:.{0,10}(?:随着|伴随着|在.{1,20}[中下])).{0,30}[，,]"), "B2", "万能状语开头"),
    (re.compile(r"(?:然而|与此同时|不可否认|显而易见|毋庸置疑|换言之)"), "B4", "论文体连接词"),
    (re.compile(r"(?:这意味着|这标志着|这代表着|这一切说明)"), "B5", "抽象总结句"),
]


# ── Gate D: Rhythm statistics ────────────────────────────────────────

def compute_rhythm(text: str) -> dict:
    """Compute paragraph/sentence length statistics."""
    paragraphs = [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]
    if not paragraphs:
        return _empty_rhythm()

    para_lens = [len(p) for p in paragraphs]
    all_sentences = []
    for p in paragraphs:
        sents = [s.strip() for s in re.split(r"[。！？；]", p) if s.strip()]
        all_sentences.extend(sents)

    sent_lens = [len(s) for s in all_sentences] if all_sentences else [0]

    # Dialogue ratio
    dialogue_paras = sum(1 for p in paragraphs if '"' in p or '"' in p or '“' in p)

    # Emotion keyword density
    emotion_kw = re.findall(r"(?:怒|愤|恨|气|喜|乐|笑|惊|怕|恐|惧|悲|伤|哭|厌|恶|烦|爽|痛快|甜|暖|温馨|冷|寒|紧张|不安)", text)

    avg_para = sum(para_lens) / len(para_lens)
    avg_sent = sum(sent_lens) / len(sent_lens)

    # Variance
    para_var = sum((x - avg_para) ** 2 for x in para_lens) / len(para_lens)

    return {
        "paragraph_count": len(para_lens),
        "avg_paragraph_len": round(avg_para, 1),
        "paragraph_len_variance": round(para_var, 1),
        "max_paragraph_len": max(para_lens),
        "sentence_count": len(sent_lens),
        "avg_sentence_len": round(avg_sent, 1),
        "max_sentence_len": max(sent_lens),
        "dialogue_ratio": round(dialogue_paras / len(para_lens), 2) if para_lens else 0,
        "emotion_kw_count": len(emotion_kw),
        "emotion_density_per_1k": round(len(emotion_kw) / (sum(para_lens) / 1000), 1) if sum(para_lens) > 0 else 0,
    }


def _empty_rhythm() -> dict:
    return {
        "paragraph_count": 0, "avg_paragraph_len": 0, "paragraph_len_variance": 0,
        "max_paragraph_len": 0, "sentence_count": 0, "avg_sentence_len": 0,
        "max_sentence_len": 0, "dialogue_ratio": 0, "emotion_kw_count": 0,
        "emotion_density_per_1k": 0,
    }


# ── Rhythm assessment ─────────────────────────────────────────────────

def assess_rhythm(stats: dict) -> list:
    findings = []
    if stats["paragraph_count"] == 0:
        return findings

    # Paragraph length
    apl = stats["avg_paragraph_len"]
    if apl > 80:
        findings.append({"gate": "D", "severity": "S3", "metric": "avg_paragraph_len",
                         "value": apl, "range": ">80", "level": "danger",
                         "msg": f"平均段落过长 ({apl}字)，建议控制在30-60字"})
    elif apl > 60:
        findings.append({"gate": "D", "severity": "S3", "metric": "avg_paragraph_len",
                         "value": apl, "range": "60-80", "level": "warning",
                         "msg": f"平均段落偏长 ({apl}字)，建议控制在30-60字"})

    # Sentence length
    asl = stats["avg_sentence_len"]
    if asl > 45:
        findings.append({"gate": "D", "severity": "S3", "metric": "avg_sentence_len",
                         "value": asl, "range": ">45", "level": "danger",
                         "msg": f"平均句子过长 ({asl}字)，建议控制在15-30字"})
    elif asl > 30:
        findings.append({"gate": "D", "severity": "S3", "metric": "avg_sentence_len",
                         "value": asl, "range": "30-45", "level": "warning",
                         "msg": f"平均句子偏长 ({asl}字)，建议控制在15-30字"})

    # Paragraph variance
    pvar = stats["paragraph_len_variance"]
    if pvar < 10:
        findings.append({"gate": "D", "severity": "S4", "metric": "paragraph_len_variance",
                         "value": pvar, "range": "<10", "level": "warning",
                         "msg": "段落长度过于均匀，可能节奏单调"})

    # Dialogue ratio
    dr = stats["dialogue_ratio"]
    if dr < 0.15:
        findings.append({"gate": "D", "severity": "S3", "metric": "dialogue_ratio",
                         "value": dr, "range": "<15%", "level": "danger",
                         "msg": f"对话段落占比过低 ({dr:.0%})，建议30-50%"})
    elif dr < 0.30:
        findings.append({"gate": "D", "severity": "S4", "metric": "dialogue_ratio",
                         "value": dr, "range": "15-30%", "level": "warning",
                         "msg": f"对话段落占比偏低 ({dr:.0%})，建议30-50%"})

    # Emotion density
    ed = stats["emotion_density_per_1k"]
    if ed < 0.5:
        findings.append({"gate": "D", "severity": "S3", "metric": "emotion_density",
                         "value": ed, "range": "<0.5/千字", "level": "danger",
                         "msg": f"情绪变化密度过低 ({ed}/千字)，建议≥1次/千字"})
    elif ed < 1.0:
        findings.append({"gate": "D", "severity": "S4", "metric": "emotion_density",
                         "value": ed, "range": "0.5-1.0/千字", "level": "warning",
                         "msg": f"情绪变化密度偏低 ({ed}/千字)，建议≥1次/千字"})

    return findings


# ── Whitelist ─────────────────────────────────────────────────────────

def load_whitelist(project_root: str) -> list:
    whitelist_path = os.path.join(project_root, ".deslop-whitelist")
    patterns = []
    if os.path.isfile(whitelist_path):
        with open(whitelist_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    try:
                        patterns.append(re.compile(line))
                    except re.error:
                        pass
    return patterns


def is_whitelisted(line: str, line_num: int, patterns: list) -> bool:
    for p in patterns:
        if p.search(line):
            return True
    return False


# ── Main check ────────────────────────────────────────────────────────

def check_file(filepath: str, intensity: str = "standard",
               project_root: Optional[str] = None) -> dict:
    path = Path(filepath)
    if not path.is_file():
        return {"error": f"File not found: {filepath}"}

    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    whitelist = load_whitelist(project_root or str(path.parent))

    findings = {"gate_a": [], "gate_b": [], "gate_d": []}

    # ── Gate A ──
    tier1_hits = []
    for pat, sev, name in GATE_A_TIER1:
        for m in pat.finditer(text):
            line_num = text[:m.start()].count("\n") + 1
            if is_whitelisted(lines[line_num - 1] if line_num <= len(lines) else "", line_num, whitelist):
                continue
            tier1_hits.append({"pattern": name, "severity": sev, "line": line_num,
                               "match": m.group()[:60]})

    findings["gate_a"].extend(tier1_hits)

    tier2_hits = []
    for pat, name, threshold in GATE_A_TIER2:
        matches = [(text[:m.start()].count("\n") + 1, m.group())
                   for m in pat.finditer(text)]
        matches = [(ln, m) for ln, m in matches
                   if not is_whitelisted(lines[ln - 1] if ln <= len(lines) else "", ln, whitelist)]
        if len(matches) >= threshold:
            tier2_hits.append({"pattern": name, "severity": 2,
                               "count": len(matches), "threshold": threshold,
                               "lines": [ln for ln, _ in matches]})

    findings["gate_a"].extend(tier2_hits)

    # Body parts / filler actions — count per chapter
    if intensity in ("standard", "deep"):
        for pat_set, label, limit, sev in [
            (GATE_A_BODY_PARTS, "身体部位万能词", 1, 3),
            (GATE_A_FILLER_ACTIONS, "万能动作", 2, 2),
        ]:
            total = 0
            for pat, name in pat_set:
                matches = [(text[:m.start()].count("\n") + 1, m.group())
                           for m in pat.finditer(text)]
                matches = [(ln, m) for ln, m in matches
                           if not is_whitelisted(lines[ln - 1] if ln <= len(lines) else "", ln, whitelist)]
                total += len(matches)
            if total > limit:
                findings["gate_a"].append({
                    "pattern": label, "severity": sev,
                    "count": total, "threshold": limit,
                    "msg": f"{label}全章出现{total}次，超过上限{limit}次"
                })

    # ── Gate B ──
    if intensity in ("standard", "deep"):
        patterns_to_check = GATE_B_PATTERNS if intensity == "deep" else [
            p for p in GATE_B_PATTERNS if p[1] in ("B1", "B4", "B5")
        ]
        for pat, gate_id, name in patterns_to_check:
            matches = [(text[:m.start()].count("\n") + 1, m.group()[:60])
                       for m in pat.finditer(text)]
            matches = [(ln, m) for ln, m in matches
                       if not is_whitelisted(lines[ln - 1] if ln <= len(lines) else "", ln, whitelist)]
            if matches:
                findings["gate_b"].append({
                    "pattern": name, "gate_id": gate_id,
                    "count": len(matches),
                    "lines": [ln for ln, _ in matches],
                    "examples": [m for _, m in matches[:3]]
                })

    # ── Gate D ──
    if intensity in ("standard", "deep"):
        stats = compute_rhythm(text)
        findings["gate_d"] = assess_rhythm(stats)
        findings["rhythm_stats"] = stats
    elif intensity == "light":
        findings["rhythm_stats"] = compute_rhythm(text)

    # ── Summary ──
    gate_a_sev = max([h["severity"] for h in findings["gate_a"]], default=0)
    gate_b_count = sum(h["count"] for h in findings["gate_b"])
    gate_d_count = len([f for f in findings["gate_d"] if f.get("level") == "danger"])

    findings["summary"] = {
        "file": str(path.name),
        "intensity": intensity,
        "char_count": len(text),
        "gate_a_hits": len(findings["gate_a"]),
        "gate_a_max_severity": gate_a_sev,
        "gate_b_hits": gate_b_count,
        "gate_d_warnings": gate_d_count,
        "verdict": "BLOCKED" if (gate_a_sev >= 5 or gate_d_count >= 3) else "WARN" if (gate_a_sev >= 3 or gate_b_count >= 2) else "PASS"
    }

    return findings


# ── Output formatters ─────────────────────────────────────────────────

def format_json(report: dict) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2)


def format_text(report: dict) -> str:
    if "error" in report:
        return f"ERROR: {report['error']}"

    lines = []
    s = report["summary"]
    lines.append(f"=== deai_check: {s['file']} ===")
    lines.append(f"字数: {s['char_count']} | 强度: {s['intensity']} | 判定: {s['verdict']}")
    lines.append(f"Gate A 禁词: {s['gate_a_hits']} hits (max severity ★{s['gate_a_max_severity']})")
    lines.append(f"Gate B 句式: {s['gate_b_hits']} hits")
    lines.append(f"Gate D 节奏: {s['gate_d_warnings']} danger warnings")
    lines.append("")

    if report["gate_a"]:
        lines.append("── Gate A: 禁词 ──")
        for h in report["gate_a"]:
            loc = f"L{h['line']}" if "line" in h else f"{h.get('count', '?')}x"
            lines.append(f"  ★{h['severity']} [{loc}] {h['pattern']}: {h.get('match', h.get('msg', ''))}")
        lines.append("")

    if report["gate_b"]:
        lines.append("── Gate B: 句式模式 ──")
        for h in report["gate_b"]:
            lines.append(f"  [{h['gate_id']}] {h['pattern']}: {h['count']}x L{h['lines']}")
            for ex in h.get("examples", [])[:2]:
                lines.append(f"    → {ex}")
        lines.append("")

    if report.get("gate_d"):
        lines.append("── Gate D: 节奏 ──")
        stats = report.get("rhythm_stats", {})
        lines.append(f"  段落: {stats.get('paragraph_count', 0)}段, 平均{stats.get('avg_paragraph_len', 0)}字, 方差{stats.get('paragraph_len_variance', 0)}")
        lines.append(f"  句子: {stats.get('sentence_count', 0)}句, 平均{stats.get('avg_sentence_len', 0)}字")
        lines.append(f"  对话比例: {stats.get('dialogue_ratio', 0):.0%}, 情绪密度: {stats.get('emotion_density_per_1k', 0)}/千字")
        for f in report["gate_d"]:
            lines.append(f"  [{f['level']}] {f['msg']}")
        lines.append("")

    return "\n".join(lines)


# ── CLI ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="De-AI six-gate checker (Gates A, B, D)")
    parser.add_argument("file", help="Path to the chapter file to check")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--intensity", choices=["light", "standard", "deep"],
                        default="standard", help="Detection intensity (default: standard)")
    parser.add_argument("--project-root", help="Project root for .deslop-whitelist lookup")
    args = parser.parse_args()

    report = check_file(args.file, args.intensity, args.project_root)

    if args.json:
        print(format_json(report))
    else:
        print(format_text(report))

    # Exit code
    if "error" in report:
        sys.exit(2)
    if report.get("summary", {}).get("verdict") == "BLOCKED":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
