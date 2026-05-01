from __future__ import annotations

import re


AUTOSAR_MACROS = [
    'FUNC',
    'P2VAR',
    'P2CONST',
    'CONST',
    'VAR',
    'FUNC_P2VAR',
]


def strip_comments_and_strings(code: str) -> str:
    code = re.sub(r'//.*?$', '', code, flags=re.MULTILINE)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    code = re.sub(r'"(?:\\.|[^"\\])*"', '""', code)
    code = re.sub(r"'(?:\\.|[^'\\])*'", "''", code)
    return code


def normalize_autosar_macros(code: str) -> str:
    for macro in AUTOSAR_MACROS:
        code = re.sub(rf'\b{macro}\s*\(([^)]*)\)', lambda m: m.group(1).split(',')[0].strip(), code)
    code = re.sub(r'\bSTATIC\b', 'static', code)
    code = re.sub(r'\bLOCAL_INLINE\b', 'static inline', code)
    return code


def preprocess_code(code: str) -> str:
    return normalize_autosar_macros(strip_comments_and_strings(code))
