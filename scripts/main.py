#!/usr/bin/env python3
"""
write-novel — AI 辅助长篇小说创作工具

Main entry point. Scripts are auxiliary; Markdown files are the truth.

Usage:
    python scripts/main.py init --project ./my-book
    python scripts/main.py search 打脸 --project ./my-book
    python scripts/main.py search --chapter 5 --volume 1 --project ./my-book
    python scripts/main.py project --project ./my-book
    python scripts/main.py doctor --project ./my-book
    python scripts/main.py preflight --chapter 5 --volume 1 --project ./my-book
    python scripts/main.py write-gate --stage gate-2 --chapter 5 --project ./my-book
    python scripts/main.py dashboard --project ./my-book
    python scripts/main.py status --project ./my-book
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.encoding_utils import ensure_nfc
from scripts.frontmatter_parser import parse_frontmatter
from scripts.project_doctor import (
    run_doctor,
    format_doctor,
    preflight,
    format_preflight,
    write_gate,
    format_write_gate,
    run_projection,
    format_projection,
)
from scripts.bm25_search import search_and_load


def get_project_root(args):
    return ensure_nfc(getattr(args, 'project', None) or os.getcwd())


def cmd_init(args):
    """Initialize a new book project with skeleton files."""
    project_root = get_project_root(args)

    dirs = [
        '人物', '世界设定', '分卷大纲', '章节草稿',
        '章节提交记录', '历史章节摘要', '写作经验', '题材模板',
    ]
    for d in dirs:
        os.makedirs(os.path.join(project_root, d), exist_ok=True)

    templates_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'skills', 'write-novel-setup', 'references', 'templates',
    )

    templates = [
        '全局写作状态.md',
        '伏笔与线索回收池.md',
    ]

    import shutil
    for tmpl in templates:
        src = os.path.join(templates_dir, tmpl)
        if os.path.isfile(src):
            dst = os.path.join(project_root, tmpl)
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
                print(f'已创建: {tmpl}')
        else:
            dst = os.path.join(project_root, tmpl)
            if not os.path.exists(dst):
                _create_minimal_template(dst, tmpl)
                print(f'已创建(最小): {tmpl}')

    print(f'\n项目已初始化: {project_root}')
    print('请编辑以下文件开始你的故事:')
    print(f'  1. {os.path.join(project_root, "全局写作状态.md")}')
    print(f'  2. {os.path.join(project_root, "世界设定/")} — 创建世界观.md')
    print(f'  3. {os.path.join(project_root, "人物/")} — 创建角色卡片')


def _create_minimal_template(filepath: str, name: str):
    """Create a minimal template file when skill templates are not available."""
    if '全局写作状态' in name:
        content = """---
主角姓名:
主角当前境界:
主角当前位置:
当前章节: 0
已完成章数: 0
已完成字数: 0
最后更新时间:
---
# 全局写作状态

## 全局系统提示词
<!-- USER_AREA_START -->

<!-- USER_AREA_END -->

## 高压线禁用词
<!-- USER_AREA_START -->

<!-- USER_AREA_END -->
"""
    elif '伏笔与线索回收池' in name:
        content = """---
总伏笔数: 0
已回收数: 0
发展中数: 0
最后更新时间:
---
# 伏笔与线索回收池

| ID | 伏笔内容 | 埋下章节 | 关联角色 | 预期回收章节 | 实际回收章节 | 状态 | 重要度 |
|----|---------|----------|---------|-------------|-------------|------|-------|
"""
    else:
        content = ''
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def cmd_search(args):
    """BM25 search for pre-writing context retrieval."""
    project_root = get_project_root(args)
    if args.chapter and args.volume:
        outline_path = ensure_nfc(os.path.join(
            project_root, '分卷大纲', f'第{args.volume}卷_细纲_第{args.chapter}章.md'
        ))
        if os.path.isfile(outline_path):
            _, body = parse_frontmatter(outline_path)
            query = body[:500]
        else:
            query = args.query or ''
    else:
        query = args.query or ''

    if not query.strip():
        print('错误: 请提供搜索关键词或使用 --chapter/--volume 指定章节')
        sys.exit(1)

    results = search_and_load(project_root, query, limit=args.limit)

    if args.json:
        json_results = [{k: v for k, v in r.items() if k != 'body'} for r in results]
        print(json.dumps(json_results, ensure_ascii=False, indent=2))
    else:
        if not results:
            print('(无搜索结果)')
            return
        for i, r in enumerate(results, 1):
            print(f'{i}. {r["file"]} (score: {r["score"]})')
            if r.get('frontmatter'):
                for k, v in r['frontmatter'].items():
                    if v and v != []:
                        print(f'   {k}: {v}')
            print()


def cmd_project(args):
    """Rebuild all .write-novel/ derived data from Markdown."""
    project_root = get_project_root(args)
    print('正在从 Markdown 重建投影...')
    result = run_projection(project_root)
    print(format_projection(result))
    print('投影重建完成。')


def cmd_doctor(args):
    """Comprehensive project health check."""
    project_root = get_project_root(args)
    result = run_doctor(project_root)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    else:
        print(format_doctor(result))
    if result['status'] == 'error':
        sys.exit(1)


def cmd_preflight(args):
    """Pre-write readiness check."""
    project_root = get_project_root(args)
    result = preflight(project_root, args.chapter or 0, args.volume or 0)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    else:
        print(format_preflight(result))
    if result['status'] == 'error':
        sys.exit(1)


def cmd_write_gate(args):
    """Write gate validation (gate-1 / gate-2 / gate-3)."""
    project_root = get_project_root(args)
    result = write_gate(project_root, args.stage, args.chapter or 0, args.volume or 0)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    else:
        print(format_write_gate(result))
    if result['status'] == 'error':
        sys.exit(1)


def cmd_dashboard(args):
    """Generate read-only dashboard HTML."""
    project_root = get_project_root(args)
    from scripts.dashboard import write_dashboard_html
    path = write_dashboard_html(project_root)
    print(f'Dashboard 已生成: {path}')


def cmd_status(args):
    """Quick project status overview."""
    project_root = get_project_root(args)
    state_path = ensure_nfc(os.path.join(project_root, '全局写作状态.md'))
    if not os.path.isfile(state_path):
        print('错误: 未找到全局写作状态.md，请先运行 init')
        sys.exit(1)
    fm, _ = parse_frontmatter(state_path)

    draft_dir = ensure_nfc(os.path.join(project_root, '章节草稿'))
    draft_count = 0
    if os.path.isdir(draft_dir):
        draft_count = len([f for f in os.listdir(draft_dir) if f.endswith('.md')])

    lines = [
        '=' * 40,
        '  write-novel 项目状态',
        '=' * 40,
        f'项目: {project_root}',
        f'主角: {fm.get("主角姓名", "?")}',
        f'当前: 第{fm.get("当前章节", "?")}章',
        f'已完成: {fm.get("已完成章数", 0)} 章 / {fm.get("已完成字数", 0)} 字',
        f'草稿文件: {draft_count} 个',
        f'最后更新: {fm.get("最后更新时间", "?")}',
        '=' * 40,
    ]
    print('\n'.join(lines))


def main():
    parser = argparse.ArgumentParser(
        description='write-novel — AI 辅助长篇小说创作工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--project', '-p', help='项目根目录（默认当前目录）')

    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # init
    p_init = subparsers.add_parser('init', help='初始化新项目')
    p_init.add_argument('--project', '-p', help='项目根目录')

    # search
    p_search = subparsers.add_parser('search', help='BM25 关键词检索')
    p_search.add_argument('--project', '-p', help='项目根目录')
    p_search.add_argument('query', nargs='?', default='', help='搜索关键词')
    p_search.add_argument('--chapter', '-c', type=int, help='按章节细纲搜索')
    p_search.add_argument('--volume', '-v', type=int, help='分卷序号')
    p_search.add_argument('--limit', type=int, default=10, help='返回数量')
    p_search.add_argument('--json', action='store_true', help='输出 JSON')

    # project
    p_project = subparsers.add_parser('project', help='从 Markdown 重建派生数据')
    p_project.add_argument('--project', '-p', help='项目根目录')

    # doctor
    p_doctor = subparsers.add_parser('doctor', help='项目健康诊断')
    p_doctor.add_argument('--project', '-p', help='项目根目录')
    p_doctor.add_argument('--json', action='store_true', help='输出 JSON')

    # preflight
    p_pre = subparsers.add_parser('preflight', help='写前预检')
    p_pre.add_argument('--project', '-p', help='项目根目录')
    p_pre.add_argument('--chapter', '-c', type=int, help='章节序号')
    p_pre.add_argument('--volume', '-v', type=int, help='分卷序号')
    p_pre.add_argument('--json', action='store_true', help='输出 JSON')

    # write-gate
    p_gate = subparsers.add_parser('write-gate', help='三段写门校验')
    p_gate.add_argument('--project', '-p', help='项目根目录')
    p_gate.add_argument('--stage', '-s', required=True, help='gate-1 / gate-2 / gate-3')
    p_gate.add_argument('--chapter', '-c', type=int, help='章节序号')
    p_gate.add_argument('--volume', '-v', type=int, help='分卷序号')
    p_gate.add_argument('--json', action='store_true', help='输出 JSON')

    # dashboard
    p_dash = subparsers.add_parser('dashboard', help='生成只读面板')
    p_dash.add_argument('--project', '-p', help='项目根目录')

    # status
    p_stat = subparsers.add_parser('status', help='查看项目状态')
    p_stat.add_argument('--project', '-p', help='项目根目录')

    args = parser.parse_args()

    if args.command == 'init':
        cmd_init(args)
    elif args.command == 'search':
        cmd_search(args)
    elif args.command == 'project':
        cmd_project(args)
    elif args.command == 'doctor':
        cmd_doctor(args)
    elif args.command == 'preflight':
        cmd_preflight(args)
    elif args.command == 'write-gate':
        cmd_write_gate(args)
    elif args.command == 'dashboard':
        cmd_dashboard(args)
    elif args.command == 'status':
        cmd_status(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
