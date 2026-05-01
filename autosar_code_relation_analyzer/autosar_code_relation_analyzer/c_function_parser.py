from __future__ import annotations

import re

from .models import FunctionDef


FUNC_SIG_RE = re.compile(
    r'(?P<sig>(?:[A-Za-z_]\w*\s+)*[A-Za-z_]\w*\s+(?P<name>[A-Za-z_]\w*)\s*\([^;{}]*\))\s*\{',
    re.MULTILINE,
)


def _find_matching_brace(text: str, open_idx: int) -> int:
    depth = 0
    for idx in range(open_idx, len(text)):
        char = text[idx]
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                return idx
    return -1


def parse_functions(file_path: str, preprocessed_code: str) -> list[FunctionDef]:
    functions: list[FunctionDef] = []
    for match in FUNC_SIG_RE.finditer(preprocessed_code):
        name = match.group('name')
        open_brace_idx = preprocessed_code.find('{', match.end() - 1)
        close_idx = _find_matching_brace(preprocessed_code, open_brace_idx)
        if close_idx < 0:
            continue
        body = preprocessed_code[open_brace_idx + 1:close_idx]
        start_line = preprocessed_code.count('\n', 0, match.start()) + 1
        end_line = preprocessed_code.count('\n', 0, close_idx) + 1
        functions.append(
            FunctionDef(
                name=name,
                file_path=file_path,
                start_line=start_line,
                end_line=end_line,
                body=body,
            )
        )
    return functions
