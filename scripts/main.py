#!/usr/bin/env python3
"""
write-novel — AI 辅助长篇小说创作工具

Main entry point for the Markdown-First web novel writing pipeline.

Usage:
    python scripts/main.py assemble --chapter 5 --volume 1 [--project ./my-book]
    python scripts/main.py continue --chapter-body-file ./ch5.txt --chapter 5 --volume 1
    python scripts/main.py status [--project ./my-book]

The pipeline operates on a project directory containing Chinese-named
Markdown files. All state is in those files — no databases, no JSON.
"""

import argparse
import os
import sys

# Add project root directory for package imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.encoding_utils import ensure_nfc
from scripts.frontmatter_parser import parse_frontmatter
from scripts.prompt_builder import assemble_prompt, save_prompt
from scripts.chapter_summarizer import generate_summary
from scripts.state_updater import run_continuation_loop
from scripts.foreshadowing_tracker import run_foreshadowing_pipeline
from scripts.diagnostics import build_status_report, dump_json, format_doctor_text, format_status_text, run_doctor
from scripts.reference_store import format_query_results, query_references
from scripts.writing_state_machine import check_stage_transition, explain_state, format_state_text, mark_stage, record_override
from scripts.dashboard import write_dashboard_data, write_dashboard_html
from scripts.guardrails import format_preflight_text, preflight_summary
from scripts.plugin_validator import format_validation_text, validate_plugin_metadata


def get_project_root(args):
    return ensure_nfc(getattr(args, 'subproject', None) or getattr(args, 'project', None) or os.getcwd())


def cmd_assemble(args):
    """Assemble the XML Prompt for a chapter and save to 当前Prompt.xml."""
    project_root = get_project_root(args)

    # Validate project structure
    state_path = os.path.join(project_root, '全局写作状态.md')
    if not os.path.isfile(state_path):
        print(f"错误：未找到 全局写作状态.md，请确认项目路径正确：{project_root}")
        sys.exit(1)

    print(f"正在组装第{args.chapter}章的 Prompt...")
    try:
        prompt = assemble_prompt(
            project_root=project_root,
            volume_num=args.volume,
            chapter_num=args.chapter,
            max_wikilink_depth=args.max_depth,
            reference_keyword=getattr(args, 'reference_keyword', '') or '',
            reference_category=getattr(args, 'reference_category', '') or '',
            reference_genre=getattr(args, 'reference_genre', '') or '',
            reference_situation=getattr(args, 'reference_situation', '') or '',
        )
    except ValueError as exc:
        print(f"错误：{exc}")
        sys.exit(1)

    output_path = save_prompt(prompt, project_root)
    print(f"Prompt 已保存至：{output_path}")
    print(f"Prompt 长度：{len(prompt)} 字符")


def cmd_continue(args):
    """Run the continuation loop after a chapter is generated."""
    project_root = get_project_root(args)

    # Read chapter body
    if args.chapter_body_file:
        with open(ensure_nfc(args.chapter_body_file), 'r', encoding='utf-8') as f:
            chapter_body = f.read()
    elif args.chapter_body:
        chapter_body = args.chapter_body
    else:
        # Try reading from stdin
        print("请输入章节正文（Ctrl+D 结束）：")
        chapter_body = sys.stdin.read()

    if not chapter_body.strip():
        print("错误：章节正文为空")
        sys.exit(1)

    chapter_title = args.title or f'第{args.chapter}章'

    print(f"正在执行第{args.chapter}章的续航闭环...")

    # Step 1: Write chapter + generate summary + update state
    loop_result = run_continuation_loop(
        project_root=project_root,
        chapter_body=chapter_body,
        chapter_title=chapter_title,
        chapter_num=args.chapter,
        volume_num=args.volume,
    )

    print(f"章节已写入：{loop_result['chapter_path']}")
    print(f"摘要已写入：{loop_result['summary_path']}")

    # Step 2: Run foreshadowing pipeline
    # Load the outline for this chapter
    outline_path = os.path.join(
        project_root, '分卷大纲', f'第{args.volume}卷_细纲_第{args.chapter}章.md'
    )
    outline_body = ''
    if os.path.isfile(ensure_nfc(outline_path)):
        _, outline_body = parse_frontmatter(outline_path)

    # Load summary
    summary_file = os.path.join(project_root, '历史章节摘要', f'第{args.chapter}章_摘要.md')
    summary_body = ''
    if os.path.isfile(ensure_nfc(summary_file)):
        with open(ensure_nfc(summary_file), 'r', encoding='utf-8') as f:
            summary_body = f.read()

    fs_result = run_foreshadowing_pipeline(
        project_root=project_root,
        outline_body=outline_body,
        summary_body=summary_body,
        chapter_num=args.chapter,
    )

    print(f"伏笔处理：注册 {len(fs_result['registered'])} 条，推进 {fs_result['advanced']} 条，回收 {fs_result['resolved']} 条")
    if fs_result['overdue']:
        print(f"⚠️ 逾期未回收伏笔：{len(fs_result['overdue'])} 条")
        for item in fs_result['overdue']:
            print(f"  - [{item['id']}] {item['content'][:40]}...（预计第{item['expected_chapter']}章回收）")

    print("续航闭环完成。")


def cmd_status(args):
    """Show project writing status."""
    project_root = get_project_root(args)
    report = build_status_report(project_root)
    if getattr(args, 'json', False):
        print(dump_json(report))
    else:
        print(format_status_text(report))


def cmd_doctor(args):
    project_root = get_project_root(args)
    result = run_doctor(project_root)
    print(dump_json(result) if args.json else format_doctor_text(result))
    if result['status'] == 'error':
        sys.exit(1)


def cmd_report(args):
    project_root = get_project_root(args)
    report = build_status_report(project_root)
    print(dump_json(report) if args.json else format_status_text(report))


def cmd_query(args):
    project_root = get_project_root(args)
    try:
        results = query_references(
            project_root,
            keyword=args.keyword or '',
            category=args.category or '',
            genre=args.genre or '',
            situation=args.situation or '',
            limit=args.limit,
        )
    except ValueError as exc:
        print(f"错误：{exc}")
        sys.exit(1)
    if args.json:
        print(dump_json({'results': results}))
    else:
        print(format_query_results(results))


def cmd_state(args):
    project_root = get_project_root(args)
    if args.override:
        if not args.reason:
            print('错误：--override 需要同时提供 --reason')
            sys.exit(1)
        path = record_override(project_root, args.volume, args.chapter, args.override, args.reason)
        print(f'override 已记录：{path}')
        return
    if args.mark:
        ok, missing = check_stage_transition(project_root, args.volume, args.chapter, args.mark)
        if not ok:
            print(f"错误：阶段 {args.mark} 缺少前置阶段：{', '.join(missing)}")
            sys.exit(1)
        path = mark_stage(project_root, args.volume, args.chapter, args.mark)
        print(f'阶段已标记：{args.mark} -> {path}')
        return
    state = explain_state(project_root, args.volume, args.chapter)
    print(dump_json(state) if args.json else format_state_text(state))


def cmd_dashboard(args):
    project_root = get_project_root(args)
    if args.data_only:
        path = write_dashboard_data(project_root)
    else:
        path = write_dashboard_html(project_root)
    print(f'dashboard 已生成：{path}')


def cmd_preflight(args):
    project_root = get_project_root(args)
    summary = preflight_summary(project_root)
    print(dump_json(summary) if args.json else format_preflight_text(summary))


def cmd_validate_plugin(args):
    project_root = get_project_root(args)
    result = validate_plugin_metadata(project_root)
    print(dump_json(result) if args.json else format_validation_text(result))
    if result['status'] == 'error':
        sys.exit(1)

def cmd_init(args):
    """Initialize a new book project with skeleton files."""
    project_root = get_project_root(args)

    # Create directory structure
    dirs = ['全局设定', '分卷大纲', '章节草稿', '人物', '世界设定', '伏笔与线索', '历史章节摘要']
    for d in dirs:
        os.makedirs(os.path.join(project_root, d), exist_ok=True)

    # Copy template files
    template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    templates = [
        '人物卡片模板.md',
        '分卷与单章细纲模板.md',
        '伏笔与线索回收池.md',
        '全局写作状态.md',
        '分卷大纲模板.md',
        '世界设定模板.md',
    ]

    import shutil
    for tmpl in templates:
        src = os.path.join(template_dir, tmpl)
        if os.path.isfile(src):
            dst = os.path.join(project_root, tmpl)
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
                print(f"已创建：{tmpl}")

    # Copy template files to subdirectories
    copy_mapping = {
        '人物卡片模板.md': '人物/',
        '分卷大纲模板.md': '分卷大纲/',
        '世界设定模板.md': '世界设定/',
    }

    for src_name, dst_dir in copy_mapping.items():
        src = os.path.join(project_root, src_name)
        dst_dir_full = os.path.join(project_root, dst_dir)
        if os.path.isfile(src):
            dst = os.path.join(dst_dir_full, os.path.basename(src))
            if not os.path.exists(dst):
                shutil.copy2(src, dst)

    print(f"\n项目已初始化：{project_root}")
    print("请编辑以下文件以开始你的故事：")
    print(f"  1. {os.path.join(project_root, '全局写作状态.md')} — 填入主角信息和写作风格")
    print(f"  2. {os.path.join(project_root, '世界设定/世界设定模板.md')} — 设计你的世界观")
    print(f"  3. {os.path.join(project_root, '人物/人物卡片模板.md')} — 创建你的角色")


def main():
    parser = argparse.ArgumentParser(
        description='write-novel — AI 辅助长篇小说创作工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python scripts/main.py init --project ./我的小说
  python scripts/main.py assemble --chapter 5 --volume 1
  python scripts/main.py continue --chapter-body-file ch5.txt --chapter 5 --volume 1
  python scripts/main.py status
        """
    )

    parser.add_argument('--project', '-p', help='项目根目录（默认为当前目录）')

    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # init
    parser_init = subparsers.add_parser('init', help='初始化新项目')
    parser_init.add_argument('--project', '-p', dest='subproject', help='项目根目录（覆盖全局 --project）')

    # assemble
    parser_asm = subparsers.add_parser('assemble', help='组装 XML Prompt')
    parser_asm.add_argument('--project', '-p', dest='subproject', help='项目根目录（覆盖全局 --project）')
    parser_asm.add_argument('--chapter', '-c', type=int, required=True, help='章节序号')
    parser_asm.add_argument('--volume', '-v', type=int, required=True, help='分卷序号')
    parser_asm.add_argument('--max-depth', '-d', type=int, default=1, help='双向链接最大加载深度')
    parser_asm.add_argument('--reference-keyword', help='注入结构化参考资料的关键词')
    parser_asm.add_argument('--reference-category', help='参考资料类别过滤')
    parser_asm.add_argument('--reference-genre', help='参考资料题材标签过滤')
    parser_asm.add_argument('--reference-situation', help='参考资料写作场景过滤')

    # continue
    parser_cont = subparsers.add_parser('continue', help='执行续航闭环')
    parser_cont.add_argument('--project', '-p', dest='subproject', help='项目根目录（覆盖全局 --project）')
    parser_cont.add_argument('--chapter', '-c', type=int, required=True, help='章节序号')
    parser_cont.add_argument('--volume', '-v', type=int, required=True, help='分卷序号')
    parser_cont.add_argument('--title', '-t', help='章节标题')
    parser_cont.add_argument('--chapter-body-file', '-f', help='章节正文文件路径')
    parser_cont.add_argument('--chapter-body', '-b', help='章节正文内容（直接输入）')

    # status
    parser_stat = subparsers.add_parser('status', help='查看项目写作状态')
    parser_stat.add_argument('--project', '-p', dest='subproject', help='项目根目录（覆盖全局 --project）')
    parser_stat.add_argument('--json', action='store_true', help='输出 JSON')

    # doctor
    parser_doc = subparsers.add_parser('doctor', help='诊断项目健康状态')
    parser_doc.add_argument('--project', '-p', dest='subproject', help='项目根目录（覆盖全局 --project）')
    parser_doc.add_argument('--json', action='store_true', help='输出 JSON')

    # report
    parser_report = subparsers.add_parser('report', help='生成写作状态报告')
    parser_report.add_argument('--project', '-p', dest='subproject', help='项目根目录（覆盖全局 --project）')
    parser_report.add_argument('--json', action='store_true', help='输出 JSON')

    # query
    parser_query = subparsers.add_parser('query', help='查询结构化写作参考资料')
    parser_query.add_argument('--project', '-p', dest='subproject', help='项目根目录（覆盖全局 --project）')
    parser_query.add_argument('keyword', nargs='?', help='关键词')
    parser_query.add_argument('--category', help='类别过滤')
    parser_query.add_argument('--genre', help='题材标签过滤')
    parser_query.add_argument('--situation', help='写作场景')
    parser_query.add_argument('--limit', type=int, default=5, help='返回数量')
    parser_query.add_argument('--json', action='store_true', help='输出 JSON')

    # state
    parser_state = subparsers.add_parser('state', help='查看或更新写作阶段状态')
    parser_state.add_argument('--project', '-p', dest='subproject', help='项目根目录（覆盖全局 --project）')
    parser_state.add_argument('--chapter', '-c', type=int, required=True, help='章节序号')
    parser_state.add_argument('--volume', '-v', type=int, required=True, help='分卷序号')
    parser_state.add_argument('--mark', help='标记完成的阶段 ID')
    parser_state.add_argument('--override', help='记录 override 的目标阶段 ID')
    parser_state.add_argument('--reason', help='override 原因')
    parser_state.add_argument('--json', action='store_true', help='输出 JSON')

    # dashboard
    parser_dashboard = subparsers.add_parser('dashboard', help='生成只读写作状态面板')
    parser_dashboard.add_argument('--project', '-p', dest='subproject', help='项目根目录（覆盖全局 --project）')
    parser_dashboard.add_argument('--data-only', action='store_true', help='只生成 dashboard JSON 数据')

    # preflight
    parser_preflight = subparsers.add_parser('preflight', help='显示运行时护栏摘要')
    parser_preflight.add_argument('--project', '-p', dest='subproject', help='项目根目录（覆盖全局 --project）')
    parser_preflight.add_argument('--json', action='store_true', help='输出 JSON')

    # validate-plugin
    parser_validate = subparsers.add_parser('validate-plugin', help='校验插件元数据和资产清单')
    parser_validate.add_argument('--project', '-p', dest='subproject', help='项目根目录（覆盖全局 --project）')
    parser_validate.add_argument('--json', action='store_true', help='输出 JSON')

    args = parser.parse_args()

    if args.command == 'init':
        cmd_init(args)
    elif args.command == 'assemble':
        cmd_assemble(args)
    elif args.command == 'continue':
        cmd_continue(args)
    elif args.command == 'status':
        cmd_status(args)
    elif args.command == 'doctor':
        cmd_doctor(args)
    elif args.command == 'report':
        cmd_report(args)
    elif args.command == 'query':
        cmd_query(args)
    elif args.command == 'state':
        cmd_state(args)
    elif args.command == 'dashboard':
        cmd_dashboard(args)
    elif args.command == 'preflight':
        cmd_preflight(args)
    elif args.command == 'validate-plugin':
        cmd_validate_plugin(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
