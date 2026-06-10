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

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scripts.encoding_utils import ensure_nfc
from scripts.frontmatter_parser import parse_frontmatter
from scripts.prompt_builder import assemble_prompt, save_prompt
from scripts.chapter_summarizer import generate_summary
from scripts.state_updater import run_continuation_loop
from scripts.foreshadowing_tracker import run_foreshadowing_pipeline


def cmd_assemble(args):
    """Assemble the XML Prompt for a chapter and save to 当前Prompt.xml."""
    project_root = ensure_nfc(args.project or os.getcwd())

    # Validate project structure
    state_path = os.path.join(project_root, '全局写作状态.md')
    if not os.path.isfile(state_path):
        print(f"错误：未找到 全局写作状态.md，请确认项目路径正确：{project_root}")
        sys.exit(1)

    print(f"正在组装第{args.chapter}章的 Prompt...")
    prompt = assemble_prompt(
        project_root=project_root,
        volume_num=args.volume,
        chapter_num=args.chapter,
        max_wikilink_depth=args.max_depth,
    )

    output_path = save_prompt(prompt, project_root)
    print(f"Prompt 已保存至：{output_path}")
    print(f"Prompt 长度：{len(prompt)} 字符")


def cmd_continue(args):
    """Run the continuation loop after a chapter is generated."""
    project_root = ensure_nfc(args.project or os.getcwd())

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
    project_root = ensure_nfc(args.project or os.getcwd())
    state_path = os.path.join(project_root, '全局写作状态.md')

    if not os.path.isfile(state_path):
        print("未找到项目文件。请先初始化项目或指定正确的路径。")
        sys.exit(1)

    fm, body = parse_frontmatter(state_path)

    print("=" * 50)
    print("  write-novel 项目写作状态")
    print("=" * 50)
    print(f"  当前分卷：第{fm.get('当前分卷', '?')}卷")
    print(f"  当前章节：第{fm.get('当前章节', '?')}章")
    print(f"  进度：{fm.get('已完成章数', 0)} 章 / {fm.get('已完成字数', 0)} 字")
    print(f"  总目标：{fm.get('总目标字数', '?')} 字")
    print(f"  主角：{fm.get('主角姓名', '?')}（{fm.get('主角当前境界', '?')}）")
    print(f"  最后更新：{fm.get('最后更新时间', '?')}")
    print("=" * 50)

    # Show foreshadowing stats if available
    fs_path = os.path.join(project_root, '伏笔与线索回收池.md')
    if os.path.isfile(fs_path):
        fs_fm, _ = parse_frontmatter(fs_path)
        print(f"  伏笔总数：{fs_fm.get('总伏笔数', 0)}")
        print(f"  已回收：{fs_fm.get('已回收数', 0)}")
        print(f"  发展中：{fs_fm.get('发展中数', 0)}")
        print("=" * 50)


def cmd_init(args):
    """Initialize a new book project with skeleton files."""
    project_root = ensure_nfc(args.project or os.getcwd())

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

    # assemble
    parser_asm = subparsers.add_parser('assemble', help='组装 XML Prompt')
    parser_asm.add_argument('--chapter', '-c', type=int, required=True, help='章节序号')
    parser_asm.add_argument('--volume', '-v', type=int, required=True, help='分卷序号')
    parser_asm.add_argument('--max-depth', '-d', type=int, default=1, help='双向链接最大加载深度')

    # continue
    parser_cont = subparsers.add_parser('continue', help='执行续航闭环')
    parser_cont.add_argument('--chapter', '-c', type=int, required=True, help='章节序号')
    parser_cont.add_argument('--volume', '-v', type=int, required=True, help='分卷序号')
    parser_cont.add_argument('--title', '-t', help='章节标题')
    parser_cont.add_argument('--chapter-body-file', '-f', help='章节正文文件路径')
    parser_cont.add_argument('--chapter-body', '-b', help='章节正文内容（直接输入）')

    # status
    parser_stat = subparsers.add_parser('status', help='查看项目写作状态')

    args = parser.parse_args()

    if args.command == 'init':
        cmd_init(args)
    elif args.command == 'assemble':
        cmd_assemble(args)
    elif args.command == 'continue':
        cmd_continue(args)
    elif args.command == 'status':
        cmd_status(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
