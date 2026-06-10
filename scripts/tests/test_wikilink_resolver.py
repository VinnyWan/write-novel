"""
Unit tests for wikilink resolver.
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.wikilink_resolver import (
    extract_wikilinks,
    resolve_wikilink_target,
    resolve_wikilinks,
    collect_linked_frontmatter,
    collect_linked_bodies,
)


class TestExtractWikilinks:
    """Tests for wikilink extraction from text."""

    def test_simple_link(self):
        text = '在[[人物/林动]]的带领下，队伍出发了。'
        links = extract_wikilinks(text)
        assert links == ['人物/林动']

    def test_multiple_links(self):
        text = '[[人物/林动]]与[[人物/沈清雪]]在[[世界设定/青云山]]相遇。'
        links = extract_wikilinks(text)
        assert links == ['人物/林动', '人物/沈清雪', '世界设定/青云山']

    def test_link_with_display_text(self):
        text = '[[人物/林动|主角林动]]决定出手。'
        links = extract_wikilinks(text)
        assert links == ['人物/林动']

    def test_link_with_anchor(self):
        text = '参考[[世界设定/力量体系#境界划分]]中的说明。'
        links = extract_wikilinks(text)
        assert links == ['世界设定/力量体系']

    def test_deduplication(self):
        text = '[[人物/林动]]出现在[[人物/林动]]面前。'
        links = extract_wikilinks(text)
        assert links == ['人物/林动']

    def test_no_links(self):
        text = '这是一段普通的叙述文字，没有任何链接。'
        links = extract_wikilinks(text)
        assert links == []

    def test_empty_text(self):
        assert extract_wikilinks('') == []

    def test_links_in_outline(self):
        text = """## 出场角色
        - [[人物/林动]]
        - [[人物/沈清雪]]
        - [[人物/萧炎]]
        """
        links = extract_wikilinks(text)
        assert len(links) == 3
        assert '人物/林动' in links
        assert '人物/萧炎' in links

    def test_wikilink_with_spaces(self):
        text = '[[人物/林 动]]'
        links = extract_wikilinks(text)
        assert links == ['人物/林 动']


class TestResolveWikilinkTarget:
    """Tests for filesystem path resolution."""

    def test_resolve_existing_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test file
            test_file = os.path.join(tmpdir, '人物', '林动.md')
            os.makedirs(os.path.dirname(test_file), exist_ok=True)
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write('---\n姓名: 林动\n---\n正文')

            result = resolve_wikilink_target('人物/林动', tmpdir)
            assert result is not None
            assert result == test_file

    def test_resolve_with_md_extension(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, '人物', '林动.md')
            os.makedirs(os.path.dirname(test_file), exist_ok=True)
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write('test')

            result = resolve_wikilink_target('人物/林动.md', tmpdir)
            assert result is not None
            assert result == test_file

    def test_resolve_nonexistent_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = resolve_wikilink_target('人物/不存在', tmpdir)
            assert result is None

    def test_resolve_empty_target(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            assert resolve_wikilink_target('', tmpdir) is None

    def test_resolve_chinese_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, '世界设定', '力量体系.md')
            os.makedirs(os.path.dirname(test_file), exist_ok=True)
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write('test')

            result = resolve_wikilink_target('世界设定/力量体系', tmpdir)
            assert result is not None
            assert os.path.basename(result) == '力量体系.md'


class TestResolveWikilinks:
    """Integration tests for full wikilink resolution pipeline."""

    def test_resolve_and_load_linked_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create linked files
            char_dir = os.path.join(tmpdir, '人物')
            os.makedirs(char_dir)

            with open(os.path.join(char_dir, '林动.md'), 'w', encoding='utf-8') as f:
                f.write('---\n姓名: 林动\n境界: 筑基期\n---\n林动是青云镇少年。')
            with open(os.path.join(char_dir, '沈清雪.md'), 'w', encoding='utf-8') as f:
                f.write('---\n姓名: 沈清雪\n境界: 金丹期\n---\n沈清雪是玄天宗弟子。')

            text = '[[人物/林动]]与[[人物/沈清雪]]相遇。'
            results = resolve_wikilinks(text, tmpdir)

            assert len(results) == 2
            names = {r['frontmatter'].get('姓名') for r in results}
            assert names == {'林动', '沈清雪'}

    def test_cycle_protection(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a file that links back to another
            char_dir = os.path.join(tmpdir, '人物')
            os.makedirs(char_dir)

            with open(os.path.join(char_dir, '林动.md'), 'w', encoding='utf-8') as f:
                f.write('---\n姓名: 林动\n---\n参见[[人物/沈清雪]]')
            with open(os.path.join(char_dir, '沈清雪.md'), 'w', encoding='utf-8') as f:
                f.write('---\n姓名: 沈清雪\n---\n参见[[人物/林动]]')

            # With max_depth=2, would normally cause infinite loop
            # But cycle protection should prevent it
            text = '[[人物/林动]]'
            results = resolve_wikilinks(text, tmpdir, max_depth=2)

            # Should have exactly 2 unique files, not infinite repeats
            loaded_paths = {r['path'] for r in results}
            assert len(loaded_paths) == 2

    def test_depth_limit(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            char_dir = os.path.join(tmpdir, '人物')
            os.makedirs(char_dir)

            with open(os.path.join(char_dir, '林动.md'), 'w', encoding='utf-8') as f:
                f.write('---\n姓名: 林动\n---\n[[人物/沈清雪]]')
            with open(os.path.join(char_dir, '沈清雪.md'), 'w', encoding='utf-8') as f:
                f.write('---\n姓名: 沈清雪\n---\n[[世界设定/青云山]]')

            ws_dir = os.path.join(tmpdir, '世界设定')
            os.makedirs(ws_dir)
            with open(os.path.join(ws_dir, '青云山.md'), 'w', encoding='utf-8') as f:
                f.write('---\n名称: 青云山\n---\n青云山很高。')

            # max_depth=1: only load directly linked files
            text = '[[人物/林动]]'
            results = resolve_wikilinks(text, tmpdir, max_depth=1)
            loaded = {r['frontmatter'].get('姓名') or r['frontmatter'].get('名称') for r in results}
            assert '林动' in loaded
            assert '沈清雪' in loaded
            # 青云山 is depth 2, should NOT be loaded with max_depth=1
            assert '青云山' not in loaded

    def test_unresolved_link_proceeds(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            text = '[[人物/不存在]]这个人不存在。'
            # Should not raise, just load nothing
            results = resolve_wikilinks(text, tmpdir)
            assert results == []

    def test_collect_linked_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            char_dir = os.path.join(tmpdir, '人物')
            os.makedirs(char_dir)
            with open(os.path.join(char_dir, '林动.md'), 'w', encoding='utf-8') as f:
                f.write('---\n姓名: 林动\n境界: 筑基期\n---\n正文')

            text = '[[人物/林动]]'
            fm_dict = collect_linked_frontmatter(text, tmpdir)
            assert '人物/林动.md' in fm_dict
            assert fm_dict['人物/林动.md'] == {'姓名': '林动', '境界': '筑基期'}

    def test_collect_linked_bodies(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            char_dir = os.path.join(tmpdir, '人物')
            os.makedirs(char_dir)
            with open(os.path.join(char_dir, '林动.md'), 'w', encoding='utf-8') as f:
                f.write('---\n姓名: 林动\n---\n林动站在山巅俯瞰众生。')

            text = '[[人物/林动]]'
            body_dict = collect_linked_bodies(text, tmpdir)
            assert '人物/林动.md' in body_dict
            assert '林动站在山巅俯瞰众生' in body_dict['人物/林动.md']
