from __future__ import annotations

from pathlib import Path

from .models import SourceFile


def should_exclude(path: Path, exclude_keywords: list[str]) -> bool:
    normalized = str(path).replace('\\', '/').lower()
    return any(word.lower() in normalized for word in exclude_keywords)


def scan_sources(src_root: str, include_headers: bool, exclude_keywords: list[str] | None = None) -> list[SourceFile]:
    root = Path(src_root)
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Invalid source directory: {src_root}")

    suffixes = {'.c'}
    if include_headers:
        suffixes.add('.h')

    exclude_keywords = exclude_keywords or []
    collected: list[SourceFile] = []
    for path in root.rglob('*'):
        if not path.is_file() or path.suffix.lower() not in suffixes:
            continue
        if should_exclude(path, exclude_keywords):
            continue
        content = path.read_text(encoding='utf-8', errors='ignore')
        collected.append(SourceFile(path=path, content=content))
    return collected
