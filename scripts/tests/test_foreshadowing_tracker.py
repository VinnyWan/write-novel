"""
Unit tests for foreshadowing tracker.
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.foreshadowing_tracker import (
    register_new_foreshadowing,
    advance_foreshadowing,
    resolve_foreshadowing,
    scan_and_advance_from_outline,
    scan_and_resolve_from_summary,
    scan_and_register_from_text,
    get_overdue_foreshadowing,
    get_foreshadowing_stats,
    run_foreshadowing_pipeline,
    STATUS_BURIED,
    STATUS_DEVELOPING,
    STATUS_RESOLVED,
)
from scripts.frontmatter_parser import parse_frontmatter


def _create_fs_pool(tmpdir: str):
    """Helper: create a minimal foreshadowing pool file."""
    fs_path = os.path.join(tmpdir, '伏笔与线索回收池.md')
    content = """---
总伏笔数: 2
已回收数: 0
发展中数: 0
逾期未回收数: 0
最后更新时间:
---

# 伏笔与线索回收池

## 伏笔总表

| 伏笔ID | 伏笔内容 | 埋设章节 | 关联人物 | 预计回收章节 | 实际回收章节 | 当前状态 | 重要度 |
|--------|---------|---------|---------|------------|------------|---------|--------|
| F001 | 山洞中的神秘古剑 | 第1章 | 林动 | 10 | | 🟡已埋 | 高 |
| F002 | 沈清雪的真实身份 | 第2章 | 沈清雪 | 15 | | 🟡已埋 | 中 |
"""
    with open(fs_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return fs_path


class TestRegisterForeshadowing:
    def test_register_new(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_fs_pool(tmpdir)

            result = register_new_foreshadowing(
                tmpdir,
                '林动体内封印的神秘力量',
                5,
                '林动',
                20,
                '高',
            )

            assert result == 'F003'

            # Verify file was updated
            fs_path = os.path.join(tmpdir, '伏笔与线索回收池.md')
            fm, body = parse_frontmatter(fs_path)
            assert fm['总伏笔数'] == 3
            assert 'F003' in body
            assert '封印的神秘力量' in body

    def test_auto_assign_id(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_fs_pool(tmpdir)

            register_new_foreshadowing(tmpdir, 'test A', 1)
            register_new_foreshadowing(tmpdir, 'test B', 2)
            register_new_foreshadowing(tmpdir, 'test C', 3)

            _, body = parse_frontmatter(
                os.path.join(tmpdir, '伏笔与线索回收池.md')
            )
            assert 'F003' in body
            assert 'F004' in body
            assert 'F005' in body


class TestAdvanceForeshadowing:
    def test_advance_to_developing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_fs_pool(tmpdir)

            count = advance_foreshadowing(tmpdir, ['F001'])

            assert count == 1

            _, body = parse_frontmatter(
                os.path.join(tmpdir, '伏笔与线索回收池.md')
            )
            # Should now show 发展中
            assert STATUS_DEVELOPING in body

    def test_advance_multiple(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_fs_pool(tmpdir)

            count = advance_foreshadowing(tmpdir, ['F001', 'F002'])
            assert count == 2


class TestResolveForeshadowing:
    def test_resolve_single(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_fs_pool(tmpdir)

            count = resolve_foreshadowing(tmpdir, ['F001'], 10)

            assert count == 1

            fm, body = parse_frontmatter(
                os.path.join(tmpdir, '伏笔与线索回收池.md')
            )
            assert fm['已回收数'] == 1
            assert STATUS_RESOLVED in body


class TestScanAndRegister:
    def test_register_from_text(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_fs_pool(tmpdir)

            text = '伏笔[F003]: 林家庄地下的秘密通道。'
            ids = scan_and_register_from_text(tmpdir, text, 5)

            assert len(ids) >= 1
            assert ids[0] == 'F003'

    def test_skip_existing_id(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_fs_pool(tmpdir)

            # F001 already exists, should be skipped
            text = '伏笔[F001]: 重复的内容。'
            ids = scan_and_register_from_text(tmpdir, text, 5)

            assert len(ids) == 0


class TestScanAndAdvance:
    def test_advance_from_outline(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_fs_pool(tmpdir)

            outline = """## 本章硬性剧本任务
            1. 林动检查古剑
            关联伏笔: F001
            """

            count = scan_and_advance_from_outline(tmpdir, outline)
            assert count == 1


class TestScanAndResolve:
    def test_resolve_from_summary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_fs_pool(tmpdir)

            summary = '回收伏笔[F001] 古剑之谜揭晓。'

            count = scan_and_resolve_from_summary(tmpdir, summary, 10)
            assert count == 1


class TestOverdueDetection:
    def test_overdue_detection(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_fs_pool(tmpdir)

            # F001 expected at ch10, current is ch12 → overdue
            overdue = get_overdue_foreshadowing(tmpdir, 12)

            assert len(overdue) >= 1
            overdue_ids = [o['id'] for o in overdue]
            assert 'F001' in overdue_ids

    def test_not_overdue_before_chapter(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_fs_pool(tmpdir)

            # F001 expected at ch10, current is ch5 → not overdue
            overdue = get_overdue_foreshadowing(tmpdir, 5)
            assert len(overdue) == 0

    def test_resolved_not_overdue(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_fs_pool(tmpdir)
            resolve_foreshadowing(tmpdir, ['F001'], 10)

            overdue = get_overdue_foreshadowing(tmpdir, 12)
            overdue_ids = [o['id'] for o in overdue]
            assert 'F001' not in overdue_ids


class TestStats:
    def test_get_stats(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_fs_pool(tmpdir)

            stats = get_foreshadowing_stats(tmpdir)
            assert stats['total'] == 2
            assert stats['resolved'] == 0


class TestFullPipeline:
    def test_complete_pipeline(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_fs_pool(tmpdir)

            outline = """## 本章硬性剧本任务
            1. 林动探索山洞发现古剑
            伏笔[F003]: 古剑内部封印着远古大能的残魂。
            关联伏笔: F001
            """

            summary = """本章核心事件：林动探索山洞发现古剑。
            回收伏笔[F001] 古剑之谜终于有了答案。
            """

            result = run_foreshadowing_pipeline(tmpdir, outline, summary, 5)

            assert len(result['registered']) >= 1
            assert result['advanced'] >= 1
            assert result['resolved'] >= 1

            # Verify file state after pipeline
            fm, _ = parse_frontmatter(
                os.path.join(tmpdir, '伏笔与线索回收池.md')
            )
            assert fm['总伏笔数'] == 3
            assert fm['已回收数'] == 1
