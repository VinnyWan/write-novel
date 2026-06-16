"""FastAPI dashboard server for write-novel project data visualization."""

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure project root is importable so "from scripts.xxx" works
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse

from scripts.encoding_utils import ensure_nfc, safe_open
from scripts.frontmatter_parser import parse_frontmatter
from scripts.project_doctor import run_doctor


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

def _safe_path(project_root: Path, rel: str) -> Path:
    """Resolve relative path safely within project_root."""
    root = project_root.resolve()
    target = (root / rel).resolve()
    target.relative_to(root)
    return target


def _exists(project_root: Path, rel: str) -> bool:
    try:
        return _safe_path(project_root, rel).exists()
    except ValueError:
        return False


def _is_file(project_root: Path, rel: str) -> bool:
    try:
        return _safe_path(project_root, rel).is_file()
    except ValueError:
        return False


def _is_dir(project_root: Path, rel: str) -> bool:
    try:
        return _safe_path(project_root, rel).is_dir()
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# Data readers
# ---------------------------------------------------------------------------

def _read_project_info(project_root: Path) -> Dict[str, Any]:
    """Read project metadata from 全局写作状态.md frontmatter."""
    state_path = _safe_path(project_root, "全局写作状态.md")
    if not state_path.is_file():
        return {"error": "全局写作状态.md 不存在"}
    fm, body = parse_frontmatter(str(state_path))
    return {
        "protagonist": fm.get("主角姓名", "未设置"),
        "protagonist_realm": fm.get("主角当前境界", "未设置"),
        "protagonist_location": fm.get("主角当前位置", "未设置"),
        "current_chapter": fm.get("当前章节", 0),
        "completed_chapters": fm.get("已完成章数", 0),
        "completed_words": fm.get("已完成字数", 0),
        "last_updated": fm.get("最后更新时间", "未记录"),
        "writing_style": fm.get("写作风格", ""),
        "current_volume": fm.get("当前分卷", ""),
    }


def _read_progress(project_root: Path) -> Dict[str, Any]:
    """Read chapter/volume progress from project files."""
    # Chapter drafts
    chapter_count = 0
    chapter_files: List[str] = []
    draft_dir = _safe_path(project_root, "章节草稿")
    if draft_dir.is_dir():
        chapters = sorted(
            [f for f in os.listdir(str(draft_dir)) if f.endswith(".md")]
        )
        chapter_count = len(chapters)
        chapter_files = chapters

    # Summaries
    summary_count = 0
    summary_dir = _safe_path(project_root, "历史章节摘要")
    if summary_dir.is_dir():
        summary_count = len(
            [f for f in os.listdir(str(summary_dir)) if f.endswith(".md")]
        )

    # Volume outlines
    volume_count = 0
    volumes: List[str] = []
    outline_dir = _safe_path(project_root, "分卷大纲")
    if outline_dir.is_dir():
        vol_files = sorted(
            [f for f in os.listdir(str(outline_dir)) if f.endswith(".md")]
        )
        volume_count = len(vol_files)
        volumes = vol_files

    # Commit records
    commit_count = 0
    commit_dir = _safe_path(project_root, "章节提交记录")
    if commit_dir.is_dir():
        commit_count = len(
            [f for f in os.listdir(str(commit_dir)) if f.endswith(".md")]
        )

    # Word count from state file
    words = 0
    state_path = _safe_path(project_root, "全局写作状态.md")
    if state_path.is_file():
        fm, _ = parse_frontmatter(str(state_path))
        words = fm.get("已完成字数", 0)

    return {
        "chapter_count": chapter_count,
        "chapter_files": chapter_files,
        "summary_count": summary_count,
        "volume_count": volume_count,
        "volume_files": volumes,
        "commit_count": commit_count,
        "completed_words": words,
    }


def _read_characters(project_root: Path) -> List[Dict[str, Any]]:
    """Read character cards from 人物/ directory."""
    char_dir = _safe_path(project_root, "人物")
    if not char_dir.is_dir():
        return []

    characters = []
    for fname in sorted(os.listdir(str(char_dir))):
        if not fname.endswith(".md"):
            continue
        fpath = char_dir / fname
        try:
            fm, _ = parse_frontmatter(str(fpath))
        except Exception:
            fm = {}

        # Derive character status from available fields
        status = "已创建"
        if fm.get("状态"):
            status = fm["状态"]

        characters.append({
            "name": fname.replace(".md", ""),
            "file": fname,
            "gender": fm.get("性别", ""),
            "age": fm.get("年龄", ""),
            "realm": fm.get("境界", "") or fm.get("修为", "") or fm.get("等级", ""),
            "identity": fm.get("身份", "") or fm.get("职业", "") or fm.get("称号", ""),
            "personality": fm.get("性格", "") or fm.get("个性", ""),
            "role": fm.get("角色定位", "") or fm.get("定位", ""),
            "status": status,
            "relation": fm.get("与主角关系", "") or fm.get("关系", ""),
        })

    return characters


def _read_foreshadowing(project_root: Path) -> Dict[str, Any]:
    """Parse 伏笔与线索回收池.md for foreshadowing lifecycle tracking."""
    fs_path = _safe_path(project_root, "伏笔与线索回收池.md")
    if not fs_path.is_file():
        return {"entries": [], "total": 0, "buried": 0, "developing": 0, "resolved": 0}

    fm, body = parse_frontmatter(str(fs_path))

    entries: List[Dict[str, Any]] = []
    # Match markdown table rows: | F001 | 内容 | 章节 | 角色 | 预期 | 实际 | 状态 | 重要度 |
    table_re = re.compile(
        r'^\|\s*(F\d+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(\d*)\s*\|\s*(\d*)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|$',
        re.MULTILINE,
    )
    for m in table_re.finditer(body):
        entries.append({
            "id": m.group(1).strip(),
            "content": m.group(2).strip(),
            "planted_chapter": m.group(3).strip(),
            "characters": m.group(4).strip(),
            "expected_chapter": int(m.group(5).strip()) if m.group(5).strip() else 0,
            "actual_chapter": int(m.group(6).strip()) if m.group(6).strip() else 0,
            "status": m.group(7).strip(),
            "importance": m.group(8).strip(),
        })

    stats = {
        "total": len(entries),
        "buried": sum(1 for e in entries if "已埋" in e["status"]),
        "developing": sum(1 for e in entries if "发展中" in e["status"]),
        "resolved": sum(1 for e in entries if "已回收" in e["status"]),
    }

    return {"entries": entries, **stats}


def _read_file_tree(project_root: Path) -> Dict[str, Any]:
    """Build a read-only file tree of the project."""
    skip_dirs = {".write-novel", ".git", ".claude", ".claude-plugin",
                 "__pycache__", ".pytest_cache", "node_modules"}
    skip_files = {".DS_Store"}
    skip_extensions = {".pyc", ".bak"}

    def walk(dir_path: Path, depth: int = 0) -> List[Dict[str, Any]]:
        if depth > 6:  # safety limit
            return []
        items: List[Dict[str, Any]] = []
        try:
            entries = sorted(dir_path.iterdir(), key=lambda p: (not p.is_dir(), p.name))
        except PermissionError:
            return []

        for entry in entries:
            name = entry.name
            if name in skip_dirs:
                continue
            if name in skip_files:
                continue
            if entry.is_file() and entry.suffix in skip_extensions:
                continue
            if name.startswith("."):
                continue

            item: Dict[str, Any] = {
                "name": name,
                "type": "directory" if entry.is_dir() else "file",
                "path": str(entry.relative_to(project_root)),
            }
            if entry.is_dir():
                item["children"] = walk(entry, depth + 1)
            else:
                try:
                    item["size"] = entry.stat().st_size
                except OSError:
                    item["size"] = 0

            items.append(item)

        return items

    return {"tree": walk(project_root)}


def _read_diagnostics(project_root: Path) -> Dict[str, Any]:
    """Run project doctor and return results."""
    result = run_doctor(str(project_root))
    return result


# ---------------------------------------------------------------------------
# HTML Dashboard
# ---------------------------------------------------------------------------

DASHBOARD_HTML = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>write-novel 写作面板</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
                 "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    background: #f0f2f5;
    color: #1f2933;
    line-height: 1.6;
  }

  /* Header */
  .header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    color: #fff;
    padding: 20px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  }
  .header h1 { font-size: 22px; font-weight: 700; letter-spacing: 0.5px; }
  .header .subtitle { font-size: 13px; opacity: 0.7; margin-top: 2px; }
  .header .status-dot {
    display: inline-block; width: 8px; height: 8px; border-radius: 50%;
    margin-right: 6px; background: #51cf66;
  }
  .header .status-dot.error { background: #ff6b6b; }
  .header .status-dot.warning { background: #ffd43b; }

  /* Container */
  .container { max-width: 1200px; margin: 0 auto; padding: 24px 32px; }

  /* Section headings */
  .section-title {
    font-size: 18px; font-weight: 600; margin: 32px 0 16px;
    padding-bottom: 8px; border-bottom: 2px solid #d9e2ec;
    display: flex; align-items: center; gap: 8px;
  }
  .section-title:first-of-type { margin-top: 0; }

  /* Metric cards grid */
  .card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 16px;
  }
  .card {
    background: #fff; border-radius: 10px; padding: 18px 20px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    transition: box-shadow 0.2s;
  }
  .card:hover { box-shadow: 0 2px 12px rgba(0,0,0,0.1); }
  .card .label { font-size: 13px; color: #60758a; margin-bottom: 6px; }
  .card .value { font-size: 28px; font-weight: 700; color: #1f2933; }
  .card .detail { font-size: 12px; color: #8a96a6; margin-top: 4px; }

  /* Status badges */
  .badge {
    display: inline-block; padding: 2px 10px; border-radius: 12px;
    font-size: 12px; font-weight: 600;
  }
  .badge-ok { background: #d3f9d8; color: #2b8a3e; }
  .badge-warning { background: #fff3bf; color: #e67700; }
  .badge-error { background: #ffe3e3; color: #c92a2a; }
  .badge-info { background: #d0ebff; color: #1864ab; }

  /* Character cards */
  .char-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 16px;
  }
  .char-card {
    background: #fff; border-radius: 10px; padding: 16px 20px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    border-left: 4px solid #4c6ef5;
    transition: box-shadow 0.2s;
  }
  .char-card:hover { box-shadow: 0 2px 12px rgba(0,0,0,0.1); }
  .char-card .char-name {
    font-size: 17px; font-weight: 700; color: #1f2933; margin-bottom: 8px;
  }
  .char-card .char-meta {
    font-size: 13px; color: #60758a; display: flex; flex-wrap: wrap; gap: 4px 12px;
  }
  .char-card .char-meta span { white-space: nowrap; }
  .char-card .char-status {
    margin-top: 8px; font-size: 12px;
  }

  /* Foreshadowing table */
  .fs-table-wrap { overflow-x: auto; }
  .fs-table {
    width: 100%; border-collapse: collapse; background: #fff;
    border-radius: 10px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    font-size: 14px;
  }
  .fs-table th {
    background: #f8f9fa; padding: 12px 14px; text-align: left;
    font-weight: 600; color: #495057; border-bottom: 2px solid #dee2e6;
    white-space: nowrap;
  }
  .fs-table td {
    padding: 10px 14px; border-bottom: 1px solid #e9ecef; vertical-align: top;
  }
  .fs-table tbody tr:hover { background: #f8f9ff; }
  .fs-table .status-buried { color: #e67700; }
  .fs-table .status-developing { color: #f08c00; }
  .fs-table .status-resolved { color: #2b8a3e; }

  /* File tree */
  .file-tree {
    background: #fff; border-radius: 10px; padding: 16px 20px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06); font-size: 14px;
    font-family: "SF Mono", "Fira Code", "Consolas", monospace;
  }
  .tree-node { cursor: pointer; user-select: none; padding: 3px 0; }
  .tree-node:hover { color: #4c6ef5; }
  .tree-children { padding-left: 20px; display: none; }
  .tree-children.open { display: block; }
  .tree-icon { display: inline-block; width: 18px; color: #868e96; }
  .tree-dir { color: #4c6ef5; font-weight: 500; }
  .tree-file { color: #495057; }

  /* Diagnostics */
  .diag-summary {
    display: flex; gap: 16px; margin-bottom: 16px; flex-wrap: wrap;
  }
  .diag-stat {
    background: #fff; border-radius: 8px; padding: 12px 20px;
    text-align: center; min-width: 80px; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  }
  .diag-stat .num { font-size: 24px; font-weight: 700; }
  .diag-stat .lbl { font-size: 12px; color: #60758a; }
  .diag-stat.ok .num { color: #2b8a3e; }
  .diag-stat.warning .num { color: #e67700; }
  .diag-stat.error .num { color: #c92a2a; }
  .diag-stat.info .num { color: #1864ab; }

  .diag-list { list-style: none; }
  .diag-item {
    background: #fff; border-radius: 8px; padding: 12px 16px; margin-bottom: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    display: flex; align-items: flex-start; gap: 12px;
  }
  .diag-icon { font-size: 16px; flex-shrink: 0; margin-top: 1px; }
  .diag-body { flex: 1; }
  .diag-path { font-weight: 600; font-size: 14px; }
  .diag-msg { font-size: 13px; color: #60758a; }
  .diag-hint { font-size: 12px; color: #868e96; font-style: italic; margin-top: 2px; }

  /* Loading / error states */
  .loading { color: #868e96; padding: 20px; text-align: center; }
  .error-msg { color: #c92a2a; padding: 20px; text-align: center; }
  .empty-state { color: #868e96; padding: 40px; text-align: center; }
  .empty-state .icon { font-size: 40px; margin-bottom: 8px; }

  /* Footer */
  .footer {
    text-align: center; padding: 24px; color: #868e96; font-size: 12px;
  }
</style>
</head>
<body>

<div class="header">
  <div>
    <h1><span class="status-dot" id="health-dot"></span>write-novel 写作面板</h1>
    <div class="subtitle" id="project-path">加载中...</div>
  </div>
  <div style="text-align:right">
    <div style="font-size:13px" id="last-updated"></div>
  </div>
</div>

<div class="container">

  <!-- Overview / 进度概览 -->
  <h2 class="section-title">&#x1F4CA; 进度概览</h2>
  <div class="card-grid" id="overview-cards">
    <div class="loading">加载中...</div>
  </div>

  <!-- Characters / 角色状态 -->
  <h2 class="section-title">&#x1F464; 角色状态</h2>
  <div class="char-grid" id="char-grid">
    <div class="loading">加载中...</div>
  </div>

  <!-- Foreshadowing / 伏笔追踪 -->
  <h2 class="section-title">&#x1F50D; 伏笔追踪</h2>
  <div class="fs-table-wrap" id="fs-table-wrap">
    <div class="loading">加载中...</div>
  </div>

  <!-- Files / 文件浏览 -->
  <h2 class="section-title">&#x1F4C1; 文件浏览</h2>
  <div class="file-tree" id="file-tree">
    <div class="loading">加载中...</div>
  </div>

  <!-- Diagnostics / 健康诊断 -->
  <h2 class="section-title">&#x1FA7A; 健康诊断</h2>
  <div id="diag-container">
    <div class="loading">加载中...</div>
  </div>

</div>

<div class="footer">
  write-novel Dashboard &mdash; 只读视图，不修改源文件 &mdash;
  <span id="footer-time"></span>
</div>

<script>
// ── Utilities ──────────────────────────────────────────────────
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(url + " " + res.status);
  return res.json();
}

// ── Render Overview ───────────────────────────────────────────
async function renderOverview() {
  const container = $("#overview-cards");
  try {
    const [info, progress] = await Promise.all([
      fetchJSON("/api/project/info"),
      fetchJSON("/api/progress"),
    ]);

    $("#project-path").textContent =
      info.project_root || (info.error ? "未初始化" : "");
    $("#last-updated").textContent =
      "最后更新: " + (info.last_updated || "?");

    const cards = [];

    if (info.protagonist) {
      cards.push({ label: "主角", value: info.protagonist,
                   detail: (info.protagonist_realm || "") + " " + (info.protagonist_location || "") });
    }
    cards.push({ label: "已完成章节", value: progress.chapter_count + " 章",
                 detail: progress.commit_count + " 条提交记录" });
    cards.push({ label: "已完成字数", value: (progress.completed_words || 0).toLocaleString(),
                 detail: progress.summary_count + " 份摘要" });
    cards.push({ label: "分卷/大纲文件", value: progress.volume_count + " 个",
                 detail: "分卷大纲" });
    cards.push({ label: "角色数量", value: "...",
                 detail: "加载中", id: "char-count-card" });

    if (info.current_chapter) {
      cards.push({ label: "当前进度", value: "第" + info.current_chapter + "章",
                   detail: info.current_volume ? "第" + info.current_volume + "卷" : "" });
    }

    container.innerHTML = cards.map(c =>
      '<div class="card"' + (c.id ? ' id="' + c.id + '"' : '') + '>' +
        '<div class="label">' + esc(c.label) + '</div>' +
        '<div class="value">' + esc(c.value) + '</div>' +
        '<div class="detail">' + esc(c.detail) + '</div>' +
      '</div>'
    ).join("");

  } catch (e) {
    container.innerHTML = '<div class="error-msg">加载失败: ' + esc(e.message) + '</div>';
  }
}

function esc(s) {
  if (s == null) return "";
  return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}

// ── Render Characters ─────────────────────────────────────────
async function renderCharacters() {
  const container = $("#char-grid");
  try {
    const chars = await fetchJSON("/api/characters");

    // Update overview card
    const cc = $("#char-count-card");
    if (cc) {
      cc.querySelector(".value").textContent = chars.length + " 人";
      cc.querySelector(".detail").textContent = "人物卡片";
    }

    if (!chars.length) {
      container.innerHTML = '<div class="empty-state"><div class="icon">&#x1F465;</div>人物/ 目录为空，创建角色卡片后在此显示。</div>';
      return;
    }

    container.innerHTML = chars.map(c => {
      const statusClass = (c.status && c.status.includes("主角")) ? "badge-ok" :
                          (c.status && c.status.includes("反派")) ? "badge-error" :
                          "badge-info";
      let meta = [];
      if (c.gender) meta.push(c.gender);
      if (c.age) meta.push(c.age + "岁");
      if (c.realm) meta.push(c.realm);
      if (c.identity) meta.push(c.identity);
      if (c.role) meta.push(c.role);
      return '<div class="char-card">' +
        '<div class="char-name">' + esc(c.name) + '</div>' +
        '<div class="char-meta">' +
          meta.map(m => '<span>' + esc(m) + '</span>').join("") +
        '</div>' +
        (c.status ? '<div class="char-status"><span class="badge ' + statusClass + '">' + esc(c.status) + '</span></div>' : '') +
      '</div>';
    }).join("");

  } catch (e) {
    container.innerHTML = '<div class="error-msg">加载失败: ' + esc(e.message) + '</div>';
  }
}

// ── Render Foreshadowing ──────────────────────────────────────
async function renderForeshadowing() {
  const container = $("#fs-table-wrap");
  try {
    const data = await fetchJSON("/api/foreshadowing");

    if (!data.total) {
      container.innerHTML = '<div class="empty-state"><div class="icon">&#x1F4ED;</div>暂无伏笔记录，开始埋下第一条伏笔吧。</div>';
      return;
    }

    const statusIcon = (s) => {
      if (/已埋/.test(s)) return '<span class="status-buried">&#x1F7E1; ' + esc(s) + '</span>';
      if (/发展中/.test(s)) return '<span class="status-developing">&#x1F7E0; ' + esc(s) + '</span>';
      if (/已回收/.test(s)) return '<span class="status-resolved">&#x1F7E2; ' + esc(s) + '</span>';
      return esc(s);
    };

    const importanceIcon = (s) => {
      if (/极高|核心/.test(s)) return '&#x2B50;&#x2B50;&#x2B50; ' + esc(s);
      if (/高|重要/.test(s)) return '&#x2B50;&#x2B50; ' + esc(s);
      if (/中/.test(s)) return '&#x2B50; ' + esc(s);
      return esc(s);
    };

    container.innerHTML =
      '<div style="margin-bottom:12px;display:flex;gap:16px;flex-wrap:wrap">' +
        '<span class="badge badge-warning">&#x1F7E1; 已埋: ' + data.buried + '</span>' +
        '<span class="badge" style="background:#ffe0b2;color:#e65100">&#x1F7E0; 发展中: ' + data.developing + '</span>' +
        '<span class="badge badge-ok">&#x1F7E2; 已回收: ' + data.resolved + '</span>' +
        '<span class="badge badge-info">总计: ' + data.total + '</span>' +
      '</div>' +
      '<table class="fs-table"><thead><tr>' +
        '<th>ID</th><th>伏笔内容</th><th>埋下章节</th><th>关联角色</th>' +
        '<th>预期回收</th><th>实际回收</th><th>状态</th><th>重要度</th>' +
      '</tr></thead><tbody>' +
      data.entries.map(e =>
        '<tr>' +
          '<td>' + esc(e.id) + '</td>' +
          '<td>' + esc(e.content) + '</td>' +
          '<td>' + esc(e.planted_chapter) + '</td>' +
          '<td>' + esc(e.characters) + '</td>' +
          '<td>' + (e.expected_chapter > 0 ? '第' + e.expected_chapter + '章' : '-') + '</td>' +
          '<td>' + (e.actual_chapter > 0 ? '第' + e.actual_chapter + '章' : '-') + '</td>' +
          '<td>' + statusIcon(e.status) + '</td>' +
          '<td>' + importanceIcon(e.importance) + '</td>' +
        '</tr>'
      ).join("") +
      '</tbody></table>';

  } catch (e) {
    container.innerHTML = '<div class="error-msg">加载失败: ' + esc(e.message) + '</div>';
  }
}

// ── Render File Tree ──────────────────────────────────────────
function renderFileTreeNode(node) {
  if (node.type === "directory") {
    const hasChildren = node.children && node.children.length > 0;
    return '<div class="tree-node" onclick="toggleTree(this)">' +
      '<span class="tree-icon">' + (hasChildren ? '&#x25B6;' : '&#x25B7;') + '</span> ' +
      '<span class="tree-dir">&#x1F4C1; ' + esc(node.name) + '</span>' +
      '</div>' +
      (hasChildren
        ? '<div class="tree-children">' +
            node.children.map(renderFileTreeNode).join("") +
          '</div>'
        : '');
  } else {
    const sizeFmt = node.size > 1024
      ? (node.size / 1024).toFixed(1) + " KB"
      : node.size + " B";
    return '<div class="tree-node">' +
      '<span class="tree-icon">&#x1F4C4;</span> ' +
      '<span class="tree-file">' + esc(node.name) +
        ' <span style="color:#adb5bd;font-size:11px">' + sizeFmt + '</span></span>' +
      '</div>';
  }
}

function toggleTree(el) {
  const icon = el.querySelector(".tree-icon");
  const children = el.nextElementSibling;
  if (children && children.classList.contains("tree-children")) {
    const isOpen = children.classList.toggle("open");
    icon.innerHTML = isOpen ? "&#x25BC;" : "&#x25B6;";
  }
}

async function renderFileTree() {
  const container = $("#file-tree");
  try {
    const data = await fetchJSON("/api/files");
    if (!data.tree || !data.tree.length) {
      container.innerHTML = '<div class="empty-state">项目目录为空</div>';
      return;
    }
    container.innerHTML = data.tree.map(renderFileTreeNode).join("");
  } catch (e) {
    container.innerHTML = '<div class="error-msg">加载失败: ' + esc(e.message) + '</div>';
  }
}

// ── Render Diagnostics ────────────────────────────────────────
async function renderDiagnostics() {
  const container = $("#diag-container");
  try {
    const data = await fetchJSON("/api/diagnostics");
    const s = data.summary || {};

    // Update header health dot
    const dot = $("#health-dot");
    dot.className = "status-dot";
    if (data.status === "error") dot.classList.add("error");
    else if (data.status === "warning") dot.classList.add("warning");

    let html = '<div class="diag-summary">' +
      '<div class="diag-stat ok"><div class="num">' + (s.ok || 0) + '</div><div class="lbl">&#x2705; 正常</div></div>' +
      '<div class="diag-stat warning"><div class="num">' + (s.warning || 0) + '</div><div class="lbl">&#x26A0;&#xFE0F; 警告</div></div>' +
      '<div class="diag-stat error"><div class="num">' + (s.error || 0) + '</div><div class="lbl">&#x274C; 错误</div></div>' +
      '<div class="diag-stat info"><div class="num">' + (s.info || 0) + '</div><div class="lbl">&#x2139;&#xFE0F; 信息</div></div>' +
      '</div>';

    if (data.checks && data.checks.length) {
      const iconMap = { ok: "✅", warning: "⚠️", error: "❌", info: "ℹ️" };
      html += '<ul class="diag-list">';
      for (const c of data.checks) {
        html += '<li class="diag-item">' +
          '<div class="diag-icon">' + (iconMap[c.status] || "") + '</div>' +
          '<div class="diag-body">' +
            '<div class="diag-path">' + esc(c.path || c.name || "") + '</div>' +
            '<div class="diag-msg">' + esc(c.message || "") + '</div>' +
            (c.hint ? '<div class="diag-hint">&#x1F4A1; ' + esc(c.hint) + '</div>' : '') +
          '</div>' +
        '</li>';
      }
      html += '</ul>';
    }

    container.innerHTML = html;

  } catch (e) {
    container.innerHTML = '<div class="error-msg">加载失败: ' + esc(e.message) + '</div>';
  }
}

// ── Init ──────────────────────────────────────────────────────
async function init() {
  $("#footer-time").textContent = new Date().toLocaleString("zh-CN");

  // Fire all fetches in parallel where possible
  renderOverview();
  renderCharacters();
  renderForeshadowing();
  renderFileTree();
  renderDiagnostics();
}

document.addEventListener("DOMContentLoaded", init);
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------

def create_app(project_root=None):
    """
    Create and configure the FastAPI dashboard app.

    Args:
        project_root: Path to the write-novel project directory (Path or str).
    """
    if project_root is None:
        # Default: parent of dashboard/ directory
        project_root = Path(__file__).resolve().parent.parent
    else:
        project_root = Path(project_root).resolve()

    if not project_root.is_dir():
        raise FileNotFoundError(f"Project root does not exist: {project_root}")

    app = FastAPI(title="write-novel Dashboard", version="1.0.0")

    # ── HTML Dashboard ─────────────────────────────────────────
    @app.get("/", response_class=HTMLResponse)
    async def index():
        return DASHBOARD_HTML

    # ── API: Project Info ──────────────────────────────────────
    @app.get("/api/project/info")
    async def project_info():
        try:
            info = _read_project_info(project_root)
            info["project_root"] = str(project_root)
            return info
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ── API: Progress ──────────────────────────────────────────
    @app.get("/api/progress")
    async def progress():
        try:
            return _read_progress(project_root)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ── API: Characters ────────────────────────────────────────
    @app.get("/api/characters")
    async def characters():
        try:
            return _read_characters(project_root)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ── API: Foreshadowing ─────────────────────────────────────
    @app.get("/api/foreshadowing")
    async def foreshadowing():
        try:
            return _read_foreshadowing(project_root)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ── API: File Tree ─────────────────────────────────────────
    @app.get("/api/files")
    async def file_tree():
        try:
            return _read_file_tree(project_root)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ── API: Diagnostics ───────────────────────────────────────
    @app.get("/api/diagnostics")
    async def diagnostics():
        try:
            return _read_diagnostics(project_root)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return app
