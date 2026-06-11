import os
import tempfile
import json
from scripts.bm25_search import build_index, search, save_index, _tokenize


def test_tokenize_chinese():
    tokens = _tokenize("林动修炼九转玄功")
    assert len(tokens) > 0


def test_tokenize_mixed():
    tokens = _tokenize("境界Level10突破")
    assert len(tokens) > 0


def test_build_index_from_temp_project():
    with tempfile.TemporaryDirectory() as tmpdir:
        char_dir = os.path.join(tmpdir, '人物')
        os.makedirs(char_dir)
        with open(os.path.join(char_dir, '林动.md'), 'w', encoding='utf-8') as f:
            f.write('---\n姓名: 林动\n境界: 筑基期\n---\n\n林动是青云宗外门弟子。')

        with open(os.path.join(tmpdir, '世界设定.md'), 'w', encoding='utf-8') as f:
            f.write('---\n世界观: 修真世界\n---\n\n青云宗位于东荒。')

        data = build_index(tmpdir)
        assert len(data['files']) == 2


def test_search_finds_relevant_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        char_dir = os.path.join(tmpdir, '人物')
        os.makedirs(char_dir)
        with open(os.path.join(char_dir, '林动.md'), 'w', encoding='utf-8') as f:
            f.write('---\n姓名: 林动\n---\n\n林动 修炼 九转玄功。')

        with open(os.path.join(char_dir, '萧炎.md'), 'w', encoding='utf-8') as f:
            f.write('---\n姓名: 萧炎\n---\n\n萧炎 是 炼药师。')

        # Third file needed so BM25 IDF is non-zero (need N>2 for IDF>0)
        with open(os.path.join(tmpdir, '杂项.md'), 'w', encoding='utf-8') as f:
            f.write('---\ntype: misc\n---\n\n无关 内容。')

        data = build_index(tmpdir)
        idx_dir = os.path.join(tmpdir, '.write-novel')
        os.makedirs(idx_dir)
        with open(os.path.join(idx_dir, 'search_index.json'), 'w', encoding='utf-8') as f:
            json.dump({
                'files': data['files'],
                'tokenized': data['tokenized'],
                'built_at': data['built_at'],
            }, f, ensure_ascii=False)

        results = search(tmpdir, '林动 九转玄功')
        assert len(results) > 0
        assert any('林动' in r['file'] for r in results)


def test_search_empty_project():
    with tempfile.TemporaryDirectory() as tmpdir:
        results = search(tmpdir, 'anything')
        assert results == []


def test_save_index():
    with tempfile.TemporaryDirectory() as tmpdir:
        char_dir = os.path.join(tmpdir, '人物')
        os.makedirs(char_dir)
        with open(os.path.join(char_dir, 'test.md'), 'w', encoding='utf-8') as f:
            f.write('---\nkey: value\n---\n\ncontent')

        out = save_index(tmpdir)
        assert os.path.isfile(out)
        assert out.endswith('search_index.json')


def test_is_index_stale():
    from scripts.bm25_search import is_index_stale
    with tempfile.TemporaryDirectory() as tmpdir:
        # No index -> stale
        assert is_index_stale(tmpdir) is True

        # Create an md file, then save index
        char_dir = os.path.join(tmpdir, '人物')
        os.makedirs(char_dir)
        with open(os.path.join(char_dir, 'test.md'), 'w', encoding='utf-8') as f:
            f.write('content')

        save_index(tmpdir)
        # Index just created -> not stale
        assert is_index_stale(tmpdir) is False
