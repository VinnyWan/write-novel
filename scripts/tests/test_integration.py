"""
Integration tests for the streamlined write-novel pipeline.
Tests the full init → search → preflight → write-gate → doctor → project → status flow.
"""

import os
import sys
import tempfile
import subprocess


_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MAIN_PY = os.path.join(_PROJECT_ROOT, 'scripts', 'main.py')


def test_init_creates_project_structure():
    """init should create all required dirs and base templates."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            [sys.executable, MAIN_PY, 'init', '--project', tmpdir],
            capture_output=True, text=True
        )
        assert result.returncode == 0
        assert os.path.isdir(os.path.join(tmpdir, '人物'))
        assert os.path.isdir(os.path.join(tmpdir, '章节提交记录'))
        assert os.path.isdir(os.path.join(tmpdir, '写作经验'))
        assert os.path.isfile(os.path.join(tmpdir, '全局写作状态.md'))
        assert os.path.isfile(os.path.join(tmpdir, '伏笔与线索回收池.md'))


def test_doctor_on_fresh_project():
    """doctor should pass on a freshly initialized project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        subprocess.run(
            [sys.executable, MAIN_PY, 'init', '--project', tmpdir],
            capture_output=True, text=True
        )
        result = subprocess.run(
            [sys.executable, MAIN_PY, 'doctor', '--project', tmpdir],
            capture_output=True, text=True
        )
        # May have wikilink warnings, but should not have errors
        assert 'error' not in result.stdout.lower() or '0 error' in result.stdout


def test_preflight_on_empty_project():
    """preflight should detect missing outline."""
    with tempfile.TemporaryDirectory() as tmpdir:
        subprocess.run(
            [sys.executable, MAIN_PY, 'init', '--project', tmpdir],
            capture_output=True, text=True
        )
        result = subprocess.run(
            [sys.executable, MAIN_PY, 'preflight', '--project', tmpdir,
             '--chapter', '1', '--volume', '1'],
            capture_output=True, text=True
        )
        # Should fail because outline doesn't exist
        assert result.returncode != 0 or 'error' in result.stdout.lower()


def test_write_gate_unknown_stage():
    """write-gate with invalid stage should error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            [sys.executable, MAIN_PY, 'write-gate', '--project', tmpdir,
             '--stage', 'gate-42'],
            capture_output=True, text=True
        )
        assert result.returncode != 0


def test_search_on_fresh_project():
    """search should not error on empty project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        subprocess.run(
            [sys.executable, MAIN_PY, 'init', '--project', tmpdir],
            capture_output=True, text=True
        )
        result = subprocess.run(
            [sys.executable, MAIN_PY, 'search', '--project', tmpdir, '测试'],
            capture_output=True, text=True
        )
        assert result.returncode == 0


def test_project_projection():
    """project should create .write-novel/ with index and state."""
    with tempfile.TemporaryDirectory() as tmpdir:
        subprocess.run(
            [sys.executable, MAIN_PY, 'init', '--project', tmpdir],
            capture_output=True, text=True
        )
        result = subprocess.run(
            [sys.executable, MAIN_PY, 'project', '--project', tmpdir],
            capture_output=True, text=True
        )
        assert result.returncode == 0
        assert os.path.isfile(os.path.join(tmpdir, '.write-novel', 'search_index.json'))
        assert os.path.isfile(os.path.join(tmpdir, '.write-novel', 'state.json'))
        assert os.path.isfile(os.path.join(tmpdir, '.write-novel', 'foreshadowing_status.json'))


def test_status_on_fresh_project():
    """status should show project info without error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        subprocess.run(
            [sys.executable, MAIN_PY, 'init', '--project', tmpdir],
            capture_output=True, text=True
        )
        result = subprocess.run(
            [sys.executable, MAIN_PY, 'status', '--project', tmpdir],
            capture_output=True, text=True
        )
        assert result.returncode == 0
        assert 'write-novel 项目状态' in result.stdout
