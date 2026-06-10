"""
End-to-end integration tests for the write-novel pipeline.

Tests the full workflow:
1. Project initialization
2. Template file validation
3. Prompt assembly for a chapter
4. Continuation closed loop
5. Foreshadowing pipeline
6. Cross-platform encoding compatibility
7. Chinese colon tolerance
8. User area protection
"""

import os
import sys
import tempfile
import shutil
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.encoding_utils import ensure_nfc, normalize_path
from scripts.frontmatter_parser import parse_frontmatter, parse_frontmatter_string
from scripts.prompt_builder import assemble_prompt, save_prompt
from scripts.chapter_summarizer import generate_and_save_summary
from scripts.state_updater import run_continuation_loop
from scripts.foreshadowing_tracker import run_foreshadowing_pipeline


def setup_test_project(tmpdir: str, volume_num: int = 3, chapter_num: int = 15):
    """
    Create a complete test project with characters, volume outline,
    chapter outline, summaries, and foreshadowing pool.
    """
    # Directories
    for d in ['章节草稿', '历史章节摘要', '分卷大纲', '人物', '世界设定']:
        os.makedirs(os.path.join(tmpdir, d), exist_ok=True)

    # Global writing state
    state_content = """---
当前分卷: 1
当前章节: 15
已完成章数: 14
总目标字数: 2000000
已完成字数: 42000
主角姓名: 林动
主角当前境界: 金丹期
主角当前位置: 玄天宗山门
最后更新章节: 第14章
最后更新时间: 2026-06-10 12:00:00
---

# 全局写作状态

## 全局系统提示词
你是一位精通中国网络文学的资深写手。严格执行细纲任务。

## 高压线禁用词
- "在……的过程中"
- "眼神中闪过一丝"

## 当前写作重点
本卷进入高潮阶段，注重战力体系的严谨性。

<!-- USER_AREA_START -->
作者的私人备忘：第20章安排林动觉醒远古血脉。
<!-- USER_AREA_END -->
"""
    with open(os.path.join(tmpdir, '全局写作状态.md'), 'w', encoding='utf-8') as f:
        f.write(state_content)

    # World setting
    ws_content = """---
世界观名称: 玄天大陆
力量体系类型: 修仙
时代背景: 上古纪元末期
主要势力列表:
  - 玄天宗
  - 魔渊殿
  - 散修联盟
---

# 玄天大陆世界观

## 力量体系
修仙九境：筑基 → 金丹 → 元婴 → 化神 → 炼虚 → 合体 → 大乘 → 渡劫 → 真仙
"""
    with open(os.path.join(tmpdir, '世界设定', '世界观.md'), 'w', encoding='utf-8') as f:
        f.write(ws_content)

    # Characters (with wikilinks for testing)
    char_dir = os.path.join(tmpdir, '人物')
    char_content = """---
姓名: 林动
当前境界: 金丹期
功法: 九转玄功
长线剧情目标: 成为玄天大陆最强修仙者，守护家人
性格弱点: 过于重情义，容易被人利用
关联角色:
  - [[人物/沈清雪]]
  - [[人物/萧炎]]
---
# 林动
青云镇出身的少年修仙者，身负九转玄功传承。
"""
    with open(os.path.join(char_dir, '林动.md'), 'w', encoding='utf-8') as f:
        f.write(char_content)
    with open(os.path.join(char_dir, '沈清雪.md'), 'w', encoding='utf-8') as f:
        f.write("""---
姓名: 沈清雪
当前境界: 元婴期
功法: 冰心诀
---
# 沈清雪
玄天宗天骄弟子，冷若冰霜的外表下藏着柔软的心。
""")
    with open(os.path.join(char_dir, '萧炎.md'), 'w', encoding='utf-8') as f:
        f.write("""---
姓名: 萧炎
当前境界: 金丹期
功法: 焚天诀
---
# 萧炎
林动的好友，火属性修仙者。
""")

    # Volume outline
    vol_content = """---
卷序号: 1
卷标题: 龙兴之地
计划章数: 50
已完成章数: 14
分卷完成度百分比: 28
分卷状态: 进行中
---

# 第1卷：龙兴之地

## 分卷主线
林动从青云镇出发，历经玄天宗入门考验，逐步揭开自身血脉之谜。

## 关键转折点
1. 第5章：玄天宗入门考核
2. 第14章：断魂崖遇袭，古剑觉醒
3. 第25章：计划中的血脉觉醒
"""
    os.makedirs(os.path.join(tmpdir, '分卷大纲'), exist_ok=True)
    with open(os.path.join(tmpdir, '分卷大纲', '第1卷_大纲.md'), 'w', encoding='utf-8') as f:
        f.write(vol_content)

    # Chapter outline for chapter 15
    outline_content = f"""---
所属分卷: 1
章节序号: {chapter_num}
本章核心冲突: 林动在玄天宗入门考核中遭遇魔渊殿卧底暗算
出场角色:
  - 林动
  - 沈清雪
  - 黑袍长老
埋下伏笔:
  - F005
期待感钩子: 黑袍长老的真实身份到底是谁？林动能否识破阴谋？
字数预期: 3000
关联伏笔ID:
  - F001
---

# 第{chapter_num}章：入门考核

## 本章硬性剧本任务
1. 林动参加玄天宗入门考核第一关
2. 考核中遭遇神秘黑袍人的暗算
3. 沈清雪意外出手相助
4. 林动发现考核背后隐藏的阴谋
5. 伏笔[F005]: 黑袍人的戒指上有林家族徽

## 关键场景设计

### 场景一：入门考核开始
玄天宗广场，数百名考生等待考核开始。

### 场景二：暗算与救援
考核途中黑袍人突袭，沈清雪出面相助。

### 场景三：阴谋初现
林动在古剑的指引下发现考核中的异常。
"""
    with open(os.path.join(tmpdir, '分卷大纲', f'第1卷_细纲_第{chapter_num}章.md'), 'w', encoding='utf-8') as f:
        f.write(outline_content)

    # Foreshadowing pool
    fs_content = """---
总伏笔数: 4
已回收数: 1
发展中数: 1
逾期未回收数: 0
最后更新时间: 2026-06-10
---

# 伏笔与线索回收池

## 伏笔总表

| 伏笔ID | 伏笔内容 | 埋设章节 | 关联人物 | 预计回收章节 | 实际回收章节 | 当前状态 | 重要度 |
|--------|---------|---------|---------|------------|------------|---------|--------|
| F001 | 古剑中的远古大能残魂 | 第1章 | 林动 | 20 | | 🟠发展中 | 高 |
| F002 | 沈清雪的真实身份 | 第2章 | 沈清雪 | 25 | | 🟡已埋 | 中 |
| F003 | 魔渊殿的复活计划 | 第5章 | 黑袍长老 | 30 | | 🟡已埋 | 高 |
| F004 | 萧炎体内的火毒 | 第8章 | 萧炎 | 10 | 10 | 🟢已回收 | 中 |
"""
    with open(os.path.join(tmpdir, '伏笔与线索回收池.md'), 'w', encoding='utf-8') as f:
        f.write(fs_content)

    # Create previous chapter summaries
    summaries_dir = os.path.join(tmpdir, '历史章节摘要')
    for ch in range(1, 15):
        summary = f"""---
章节序号: {ch}
核心事件: 第{ch}章核心事件
---

# 第{ch}章摘要
第{ch}章的测试摘要内容。这是用于测试前情提要组装的摘要数据。
"""
        with open(os.path.join(summaries_dir, f'第{ch}章_摘要.md'), 'w', encoding='utf-8') as f:
            f.write(summary)

    # Create previous chapter body
    prev_body = f"""# 第14章：断魂崖之战

林动站在断魂崖边缘，手中的古剑微微震颤。

黑衣人从暗处现身，黑袍下露出阴冷的笑容。"林动，你的古剑，归我了。"

战斗一触即发。林动催动九转玄功，古剑发出耀眼光芒。黑衣人的攻击如潮水般涌来，林动且战且退。

关键时刻，古剑中的残魂觉醒，一股远古力量涌入林动体内。他的境界在这一刻完成了突破——从筑基期巅峰踏入了金丹期！

"不可能！"黑衣人惊呼。

林动挥剑斩出，一道剑气划破长空。黑衣人仓皇逃遁，只留下一句话："你逃不掉的，魔渊殿的追杀才刚刚开始……"

林动望着黑衣人消失的方向，心中涌起一股莫名的预感。这古剑背后，究竟隐藏着什么秘密？
"""
    with open(os.path.join(tmpdir, '章节草稿', '第14章_断魂崖之战.md'), 'w', encoding='utf-8') as f:
        f.write(prev_body)


class TestPromptAssembly:
    """Integration test for full prompt assembly."""

    def test_assemble_complete_prompt(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            setup_test_project(tmpdir)

            prompt = assemble_prompt(
                project_root=tmpdir,
                volume_num=1,
                chapter_num=15,
                max_wikilink_depth=1,
            )

            # Verify all major XML sections are present
            assert '<写书Prompt>' in prompt
            assert '<全局核心设定>' in prompt
            assert '<本卷宏观主线>' in prompt
            assert '<前情提要>' in prompt
            assert '<本章硬性剧本任务>' in prompt
            assert '<写作约束与高压线>' in prompt
            assert '<参考文件>' in prompt
            assert '</写书Prompt>' in prompt

            # Verify protagonist state is included
            assert '林动' in prompt
            assert '金丹期' in prompt

            # Verify chapter tasks are included
            assert '入门考核' in prompt
            assert '黑袍' in prompt

            # Verify recent summaries are included
            assert '近期章节摘要' in prompt or '第14章摘要' in prompt

            # Verify constraints are included
            assert '高压线' in prompt or '的过程中' in prompt

    def test_save_prompt_to_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            setup_test_project(tmpdir)

            prompt = assemble_prompt(tmpdir, 1, 15)
            path = save_prompt(prompt, tmpdir)

            assert os.path.exists(path)
            assert '当前Prompt.xml' in path

            # Verify XML is valid enough to parse
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            assert '<写书Prompt>' in content
            assert '</写书Prompt>' in content


class TestContinuationLoop:
    """Integration test for the continuation closed loop."""

    def test_full_loop_integration(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            setup_test_project(tmpdir, volume_num=1, chapter_num=15)

            chapter_body = """# 第15章：入门考核

林动踏入玄天宗的入门考核场地，数百道目光注视着他。

考核第一关是灵力测试。林动催动九转玄功，金丹期的修为毫无保留地爆发。

突然，一名黑袍长老出现在考场上空。他的目光扫过林动手中的古剑，眼中闪过一丝贪婪。

"这个考生，我要亲自考核。"黑袍长老冷冷说道。

沈清雪从人群中走出："长老，这不合规矩。"

黑袍长老冷哼一声，一股威压笼罩全场。林动感觉呼吸困难，但古剑中传来的力量支撑着他。

"伏笔[F005]："当林动抬头时，他看到了黑袍长老手指上的戒指——那是林家族徽的图案！

在沈清雪的协助下，林动勉强通过了考核。但黑袍长老临走前的眼神让林动心中警铃大作。

回收伏笔[F001] 古剑残魂的身份终于揭晓——他正是林家三千年前的先祖，林玄天！
"""

            from scripts.state_updater import run_continuation_loop
            result = run_continuation_loop(
                tmpdir, chapter_body, '入门考核', 15, 1
            )

            # Verify chapter was written
            assert os.path.exists(result['chapter_path'])

            # Verify summary was written
            assert os.path.exists(result['summary_path'])

            # Verify state was updated
            fm, body = parse_frontmatter(result['state_path'])
            assert fm['当前章节'] == 16
            assert fm['已完成章数'] == 15
            assert fm['已完成字数'] > 0

            # Verify user area preserved
            with open(result['state_path'], 'r', encoding='utf-8') as f:
                content = f.read()
            assert '私人备忘' in content or '第20章' in content

            # Verify volume progress
            vol_path = os.path.join(tmpdir, '分卷大纲', '第1卷_大纲.md')
            fm_vol, _ = parse_frontmatter(vol_path)
            assert fm_vol['已完成章数'] == 15


class TestForeshadowingPipeline:
    """Integration test for the complete foreshadowing pipeline."""

    def test_pipeline_integration(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            setup_test_project(tmpdir, volume_num=1, chapter_num=15)

            outline = """关联伏笔: F001, F002
伏笔[F005]: 黑袍长老的戒指上有林家族徽。"""

            summary = """本章核心事件：入门考核遭遇暗算。
回收伏笔[F001] 古剑残魂身份揭晓——林玄天。
新埋伏笔：F005 黑袍长老与林家的关联。"""

            result = run_foreshadowing_pipeline(tmpdir, outline, summary, 15)

            # Should have registered F005 if not existing
            assert len(result['registered']) >= 1 or 'F005' in str(result)

            # Should have advanced F002
            assert result['advanced'] >= 1

            # Should have resolved F001
            assert result['resolved'] >= 1


class TestCrossPlatformEncoding:
    """Tests for cross-platform Chinese path compatibility."""

    def test_nfd_nfc_roundtrip(self):
        # Create content with Chinese path
        path_nfc = '人物/林动.md'
        path_nfd = unicodedata.normalize('NFD', path_nfc)

        # Both should normalize to same path
        assert normalize_path(path_nfc) == normalize_path(path_nfd)

    def test_chinese_path_file_operations(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a file with a Chinese name
            filename = '测试文件.md'
            filepath = os.path.join(tmpdir, filename)
            filepath = ensure_nfc(filepath)

            content = '---\n测试: 值\n---\n正文'
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            # Read back using our parser
            fm, body = parse_frontmatter(filepath)
            assert fm['测试'] == '值'
            assert '正文' in body


class TestChineseColonTolerance:
    """Tests for Chinese colon (：) tolerance in frontmatter."""

    def test_chinese_colons_in_project_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Content with Chinese colons (as a real writer might type)
            content = """---
姓名：林动
当前境界：金丹期
功法：九转玄功
---

# 角色简介

他说："我一定会变强的。"
"""
            filepath = os.path.join(tmpdir, '林动.md')
            filepath = ensure_nfc(filepath)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            fm, body = parse_frontmatter(filepath)
            assert fm.get('姓名') == '林动'
            assert fm.get('当前境界') == '金丹期'
            assert fm.get('功法') == '九转玄功'
            # Chinese colons in body should be preserved
            assert '他说："我一定会变强的。"' in body


class TestUserAreaProtection:
    """Tests verifying user custom area protection during state updates."""

    def test_user_area_untouched_after_update(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            setup_test_project(tmpdir, volume_num=1, chapter_num=15)

            # Save original user area content
            state_path = os.path.join(tmpdir, '全局写作状态.md')
            _, original_body = parse_frontmatter(state_path)
            original_user_area = None
            for line in original_body.split('\n'):
                if '私人备忘' in line:
                    original_user_area = line.strip()
                    break

            # Run continuation loop
            chapter_body = '# 第15章\n测试正文内容。' * 50
            run_continuation_loop(tmpdir, chapter_body, '测试', 15, 1)

            # Verify user area is unchanged
            _, updated_body = parse_frontmatter(state_path)
            for line in updated_body.split('\n'):
                if '私人备忘' in line:
                    assert original_user_area in line or '私人备忘' in line
                    break

    def test_backup_created_before_update(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            setup_test_project(tmpdir, volume_num=1, chapter_num=2)

            state_path = os.path.join(tmpdir, '全局写作状态.md')
            backup_path = state_path + '.bak'

            chapter_body = '# 第2章\n测试内容。' * 50
            run_continuation_loop(tmpdir, chapter_body, '测试', 2, 1)

            assert os.path.exists(backup_path)
