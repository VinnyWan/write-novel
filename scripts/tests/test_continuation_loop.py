"""
Unit tests for chapter summarizer and state updater.
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.chapter_summarizer import (
    generate_summary,
    write_summary,
    generate_and_save_summary,
    _split_sentences,
    _extract_key_events,
    _detect_character_changes,
    _detect_new_foreshadowing,
    _detect_resolved_foreshadowing,
)
from scripts.state_updater import (
    backup_file,
    update_global_state,
    update_volume_progress,
    write_chapter_file,
    count_chinese_chars,
    _rebuild_markdown_with_frontmatter,
)
from scripts.frontmatter_parser import parse_frontmatter


class TestSentenceSplitter:
    def test_split_chinese_sentences(self):
        text = '林动站在山巅。他俯瞰着脚下的青云镇。风吹过他的衣袍。'
        sentences = _split_sentences(text)
        assert len(sentences) >= 2
        assert any('林动' in s for s in sentences)

    def test_filter_short_sentences(self):
        text = '嗯。好的。林动决定下山前往青云镇寻找答案。'
        sentences = _split_sentences(text)
        # "嗯" and "好的" should be filtered (< 5 chars)
        assert len(sentences) == 1


class TestEventExtraction:
    def test_extract_key_events(self):
        sentences = [
            '林动突破了筑基期瓶颈成功进入金丹期',
            '他与沈清雪在断魂崖前遭遇了黑衣人的伏击',
            '战斗中林动领悟了九转玄功第三层',
            '战斗结束后两人决定前往玄天宗求援',
            '途中林动发现了一个惊天秘密',
        ]
        events = _extract_key_events(sentences)
        assert len(events) <= 3
        assert len(events) >= 1


class TestCharacterChangeDetection:
    def test_detect_breakthrough(self):
        text = '林动终于突破到了金丹期，浑身气势暴涨。'
        changes = _detect_character_changes(text)
        assert '林动' in changes
        assert '金丹期' in changes

    def test_detect_death(self):
        text = '老者说完最后一句话便气绝身亡。'
        changes = _detect_character_changes(text)
        assert '身亡' in changes

    def test_no_changes(self):
        text = '阳光洒在小镇上，一切都是那么宁静祥和。'
        changes = _detect_character_changes(text)
        assert changes == '无显著变化'


class TestForeshadowingDetection:
    def test_explicit_foreshadowing_marker(self):
        text = '伏笔[F001]: 林动发现山洞中的古剑散发着诡异的光芒。'
        results = _detect_new_foreshadowing(text)
        assert len(results) >= 1
        assert 'F001' in results[0]

    def test_heuristic_foreshadowing(self):
        text = '林动隐约感觉到有人在暗中窥视着他的一举一动。'
        results = _detect_new_foreshadowing(text)
        assert len(results) >= 1

    def test_resolved_foreshadowing(self):
        text = '回收伏笔[F001] 原来那把古剑正是失传已久的诛仙剑！'
        results = _detect_resolved_foreshadowing(text)
        assert 'F001' in results


class TestGenerateSummary:
    def test_full_summary_generation(self):
        body = """林动突破至金丹期。他与沈清雪在断魂崖遭遇伏击。
战斗中林动领悟九转玄功第三层。战后两人前往玄天宗求援。
伏笔[F005]: 林动隐约感觉有人在暗中注视着他。
回收伏笔[F001] 古剑之谜终于揭晓。"""
        summary = generate_summary(body)

        assert 'full_summary' in summary
        assert 'events' in summary
        assert 'new_foreshadowing' in summary

        # Full summary should be ~200 chars
        full = summary['full_summary']
        assert len(full) >= 50  # At least somewhat substantive


class TestWriteSummary:
    def test_write_summary_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            summary_dir = os.path.join(tmpdir, '历史章节摘要')
            os.makedirs(summary_dir)

            summary_dict = {
                'events': '林动突破至金丹期',
                'character_changes': '林动突破至金丹期',
                'new_foreshadowing': 'F005: 暗中注视',
                'resolved_foreshadowing': 'F001',
                'full_summary': '本章核心事件：林动突破至金丹期。新埋伏笔：F005。回收伏笔：F001。',
            }

            # Patch write_summary to use tmpdir
            path = write_summary(summary_dict, tmpdir, 1)
            assert os.path.exists(path)
            assert '第1章_摘要.md' in path


class TestBackupFile:
    def test_backup_created(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, 'test.md')
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write('content')

            backup = backup_file(test_file)
            assert backup is not None
            assert backup.endswith('.bak')
            assert os.path.exists(backup)

    def test_backup_nonexistent(self):
        backup = backup_file('/nonexistent/path/file.md')
        assert backup is None


class TestUpdateGlobalState:
    def test_update_basic_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create state file
            state_path = os.path.join(tmpdir, '全局写作状态.md')
            content = """---
当前章节: 5
已完成章数: 4
已完成字数: 12000
主角姓名: 林动
主角当前境界: 筑基期
---

# 全局写作状态

## 全局系统提示词
测试提示词

<!-- USER_AREA_START -->
用户自定义指令保留区
<!-- USER_AREA_END -->
"""
            with open(state_path, 'w', encoding='utf-8') as f:
                f.write(content)

            update_global_state(tmpdir, 5, 3000, '第五章标题')

            # Read back and verify
            fm, body = parse_frontmatter(state_path)
            assert fm['当前章节'] == 6
            assert fm['已完成章数'] == 5
            assert fm['已完成字数'] == 15000
            assert fm['主角姓名'] == '林动'  # unchanged

    def test_user_area_preserved(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = os.path.join(tmpdir, '全局写作状态.md')
            content = """---
当前章节: 3
已完成章数: 2
已完成字数: 6000
---

# 状态

<!-- USER_AREA_START -->
我的私人笔记：主角觉醒在第10章。
这是一个作者备忘。
<!-- USER_AREA_END -->

## 提示词
"""
            with open(state_path, 'w', encoding='utf-8') as f:
                f.write(content)

            update_global_state(tmpdir, 3, 3000, 'test')

            with open(state_path, 'r', encoding='utf-8') as f:
                updated = f.read()

            assert '私人笔记：主角觉醒在第10章' in updated
            assert '作者备忘' in updated


class TestUpdateVolumeProgress:
    def test_volume_progress_update(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            vol_dir = os.path.join(tmpdir, '分卷大纲')
            os.makedirs(vol_dir)
            vol_path = os.path.join(vol_dir, '第1卷_大纲.md')
            content = """---
卷序号: 1
计划章数: 10
已完成章数: 3
分卷完成度百分比: 30
---
# 第1卷
"""
            with open(vol_path, 'w', encoding='utf-8') as f:
                f.write(content)

            update_volume_progress(tmpdir, 1, 4)

            fm, _ = parse_frontmatter(vol_path)
            assert fm['已完成章数'] == 4
            assert fm['分卷完成度百分比'] == 40.0


class TestWriteChapterFile:
    def test_write_new_chapter(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            draft_dir = os.path.join(tmpdir, '章节草稿')
            os.makedirs(draft_dir)

            body = '# 第一章\n正文内容'
            path = write_chapter_file(body, '序章', tmpdir, 1)
            assert os.path.exists(path)
            with open(path, 'r', encoding='utf-8') as f:
                assert '正文内容' in f.read()

    def test_avoid_overwrite_with_version_suffix(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            draft_dir = os.path.join(tmpdir, '章节草稿')
            os.makedirs(draft_dir)

            # Write first version
            path1 = write_chapter_file('# v1', '序章', tmpdir, 1)
            # Write second version — should not overwrite
            path2 = write_chapter_file('# v2', '序章', tmpdir, 1)

            assert path1 != path2
            assert 'v2' in os.path.basename(path2)


class TestCountChineseChars:
    def test_count_chinese(self):
        text = '林动站在山巅俯瞰众生。'
        count = count_chinese_chars(text)
        assert count > 5

    def test_ignore_punctuation(self):
        text = '——他说："你好。"'
        count = count_chinese_chars(text)
        assert count >= 3  # 他 说 你 好


class TestRebuildMarkdown:
    def test_rebuild(self):
        fm = {'姓名': '林动', '境界': '金丹期', '关联': ['沈清雪', '萧炎']}
        body = '# 正文\n内容'
        result = _rebuild_markdown_with_frontmatter(fm, body)

        assert result.startswith('---\n')
        assert '姓名: 林动' in result
        assert '境界: 金丹期' in result
        assert '# 正文' in result
        assert '内容' in result


class TestContinuationLoop:
    def test_full_loop(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Set up project skeleton
            os.makedirs(os.path.join(tmpdir, '章节草稿'))
            os.makedirs(os.path.join(tmpdir, '历史章节摘要'))
            os.makedirs(os.path.join(tmpdir, '分卷大纲'))

            # Create global state
            state_path = os.path.join(tmpdir, '全局写作状态.md')
            with open(state_path, 'w', encoding='utf-8') as f:
                f.write("""---
当前章节: 1
已完成章数: 0
已完成字数: 0
主角姓名: 林动
主角当前境界: 筑基期
---

# 状态

<!-- USER_AREA_START -->
作者备忘
<!-- USER_AREA_END -->
""")

            # Create volume outline
            vol_path = os.path.join(tmpdir, '分卷大纲', '第1卷_大纲.md')
            with open(vol_path, 'w', encoding='utf-8') as f:
                f.write("""---
卷序号: 1
计划章数: 50
已完成章数: 0
分卷完成度百分比: 0
---
# 第1卷
""")

            # Run the loop
            from scripts.state_updater import run_continuation_loop

            chapter_body = """# 第一章 序章

林动站在山巅俯瞰青云镇，心中涌起一股豪情。

他刚刚突破筑基期第三层，实力大增。伏笔[F001]: 他隐约感觉山下有什么在召唤他。
"""
            result = run_continuation_loop(
                tmpdir, chapter_body, '序章', 1, 1
            )

            # Verify chapter was written
            assert os.path.exists(result['chapter_path'])

            # Verify summary was written
            assert os.path.exists(result['summary_path'])

            # Verify state was updated
            fm, _ = parse_frontmatter(result['state_path'])
            assert fm['当前章节'] == 2
            assert fm['已完成章数'] == 1
            assert fm['已完成字数'] > 0

            # Verify user area preserved
            with open(result['state_path'], 'r', encoding='utf-8') as f:
                assert '作者备忘' in f.read()

            # Verify volume progress
            fm_vol, _ = parse_frontmatter(result['volume_path'])
            assert fm_vol['已完成章数'] == 1
