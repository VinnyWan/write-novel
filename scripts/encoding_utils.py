"""
Unicode normalization utilities for cross-platform Chinese filename compatibility.

macOS uses NFD (decomposed) while Windows/Linux use NFC (composed).
This module normalizes all paths to NFC to ensure consistent file I/O.
"""

import unicodedata
import os
import sys


def normalize_path(path: str) -> str:
    """Normalize a file path to NFC form for cross-platform consistency."""
    if not path:
        return path
    return unicodedata.normalize('NFC', path)


def normalize_path_nfd(path: str) -> str:
    """Normalize a file path to NFD form (useful for macOS native interop)."""
    if not path:
        return path
    return unicodedata.normalize('NFD', path)


def ensure_nfc(path: str) -> str:
    """
    Ensure a path is in NFC form.
    If it's NFD, convert to NFC and log the conversion.
    """
    if not path:
        return path

    nfc = unicodedata.normalize('NFC', path)
    if nfc != path:
        print(f"[encoding_utils] NFD → NFC normalized: {path[:80]}...")
    return nfc


def normalize_path_parts(path: str) -> str:
    """Normalize each component of a path separately."""
    if not path:
        return path

    parts = path.replace('\\', '/').split('/')
    normalized = [unicodedata.normalize('NFC', p) for p in parts]
    return '/'.join(normalized)


def is_normalized_nfc(path: str) -> bool:
    """Check if a path is already in NFC form."""
    return unicodedata.normalize('NFC', path) == path


def safe_open(filepath: str, mode: str = 'r', encoding: str = 'utf-8', **kwargs):
    """
    Open a file with automatic NFC path normalization.
    Safe replacement for built-in open() when dealing with Chinese paths.
    """
    normalized = ensure_nfc(filepath)
    return open(normalized, mode=mode, encoding=encoding, **kwargs)


def safe_exists(filepath: str) -> bool:
    """Check if a path exists with NFC normalization."""
    return os.path.exists(ensure_nfc(filepath))


def safe_isdir(filepath: str) -> bool:
    """Check if a path is a directory with NFC normalization."""
    return os.path.isdir(ensure_nfc(filepath))
