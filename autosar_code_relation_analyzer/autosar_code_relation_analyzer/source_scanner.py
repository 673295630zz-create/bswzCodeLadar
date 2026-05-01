from __future__ import annotations

from pathlib import Path

from .models import SourceFile


DEFAULT_EXCLUDES = {'.git', '.svn', '.hg', 'build', 'output', 'generated', 'dist'}


def should_exclude(path: Path, exclude_keywords: set[str]) -> bool:
    normalized = str(path).replace('\\', '/').lower()
    return any(word in normalized for word in exclude_keywords)


def scan_sources(src_root: str, include_headers: bool = True, exclude_keywords: list[str] | None = None) -> list[SourceFile]:
    """Recursively scan all source files in src_root.

    By default this function scans both .c and .h files in all subfolders.
    """
    root = Path(src_root)
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Invalid source directory: {src_root}")

    suffixes = {'.c', '.h'} if include_headers else {'.c'}
    excludes = {k.lower() for k in (exclude_keywords or [])} | DEFAULT_EXCLUDES

    collected: list[SourceFile] = []
    for path in root.rglob('*'):
        if not path.is_file() or path.suffix.lower() not in suffixes:
            continue
        if should_exclude(path, excludes):
            continue
        content = path.read_text(encoding='utf-8', errors='ignore')
        collected.append(SourceFile(path=path, content=content))

    collected.sort(key=lambda x: str(x.path))
    return collected
