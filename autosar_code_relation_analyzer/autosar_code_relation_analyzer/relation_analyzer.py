from __future__ import annotations

import re

from .models import AnalysisResult, FunctionDef, RelationEdge, SourceFile

C_KEYWORDS = {'if', 'while', 'for', 'switch', 'return', 'sizeof', 'typedef', 'struct', 'union', 'enum'}
CALL_RE = re.compile(r'\b([A-Za-z_]\w*)\s*\(')
TOKEN_RE = re.compile(r'\b[A-Za-z_]\w*(?:->\w+|\.\w+)?\b')
ASSIGN_RE = re.compile(r'\b([A-Za-z_]\w*(?:->\w+|\.\w+)?)\s*=\s*([^;]+);')
RW_ASSIGN_RE = re.compile(r'\b([A-Za-z_]\w*(?:->\w+|\.\w+)?)\s*[+\-*/%&|^]=')
INC_RE = re.compile(r'(\+\+|--)\s*([A-Za-z_]\w*(?:->\w+|\.\w+)?)|([A-Za-z_]\w*(?:->\w+|\.\w+)?)\s*(\+\+|--)')


def collect_candidate_globals(contents: list[str]) -> set[str]:
    candidates: set[str] = set()
    decl = re.compile(r'^(?!\s*(if|for|while|switch|return)\b)\s*(?:static\s+)?(?:const\s+)?[A-Za-z_]\w*(?:\s+\**)?\s+([A-Za-z_]\w*)\s*(?:=[^;]*)?;', re.MULTILINE)
    for text in contents:
        for m in decl.finditer(text):
            if m.group(1):
                candidates.add(m.group(1))
        for prefix in re.findall(r'\b(g_[A-Za-z_]\w*|[A-Z][A-Za-z0-9_]*_[A-Za-z]\w*)\b', text):
            candidates.add(prefix)
    return candidates


def _normalize_var(token: str) -> str:
    return token.replace('->', '.')


def analyze_relations(source_root: str, sources: list[SourceFile], functions: list[FunctionDef], variables: list[str] | None) -> AnalysisResult:
    result = AnalysisResult(source_root=source_root, source_files=[str(s.path) for s in sources], functions=functions)
    defined = {f.name for f in functions}
    variable_filter = set(variables) if variables else collect_candidate_globals([s.content for s in sources])

    call_edges: set[tuple[str, str, str, str]] = set()
    var_edges: set[tuple[str, str, str, str, int | None]] = set()

    for fn in functions:
        lines = fn.body.splitlines()
        for call in CALL_RE.finditer(fn.body):
            callee = call.group(1)
            if callee in C_KEYWORDS:
                continue
            call_edges.add((fn.name, callee, 'calls', fn.file_path))
            if callee not in defined:
                result.external_functions.add(callee)

        for line_no, line in enumerate(lines, start=fn.start_line):
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            for m in RW_ASSIGN_RE.finditer(stripped):
                var = _normalize_var(m.group(1))
                if not variable_filter or var in variable_filter or var.split('.')[0] in variable_filter:
                    var_edges.add((fn.name, var, 'read_writes', fn.file_path, line_no))
                    result.variables.add(var)
            for m in INC_RE.finditer(stripped):
                var = _normalize_var(m.group(2) or m.group(3))
                if not variable_filter or var in variable_filter or var.split('.')[0] in variable_filter:
                    var_edges.add((fn.name, var, 'read_writes', fn.file_path, line_no))
                    result.variables.add(var)
            for m in ASSIGN_RE.finditer(stripped):
                lhs = _normalize_var(m.group(1))
                rhs = m.group(2)
                if not variable_filter or lhs in variable_filter or lhs.split('.')[0] in variable_filter:
                    var_edges.add((fn.name, lhs, 'writes', fn.file_path, line_no))
                    result.variables.add(lhs)
                for tok in TOKEN_RE.findall(rhs):
                    tok_n = _normalize_var(tok)
                    if tok_n == lhs:
                        continue
                    if not variable_filter or tok_n in variable_filter or tok_n.split('.')[0] in variable_filter:
                        var_edges.add((fn.name, tok_n, 'reads', fn.file_path, line_no))
                        result.variables.add(tok_n)
            for addr in re.findall(r'&\s*([A-Za-z_]\w*(?:->\w+|\.\w+)?)', stripped):
                var = _normalize_var(addr)
                if not variable_filter or var in variable_filter or var.split('.')[0] in variable_filter:
                    var_edges.add((fn.name, var, 'passed_by_address', fn.file_path, line_no))
                    result.variables.add(var)
            if stripped.startswith(('if', 'while', 'switch', 'return')):
                for tok in TOKEN_RE.findall(stripped):
                    tok_n = _normalize_var(tok)
                    if not variable_filter or tok_n in variable_filter or tok_n.split('.')[0] in variable_filter:
                        var_edges.add((fn.name, tok_n, 'reads', fn.file_path, line_no))
                        result.variables.add(tok_n)

    result.call_relations = [RelationEdge(*e, line_hint=None) for e in sorted(call_edges)]
    result.variable_relations = [RelationEdge(*e) for e in sorted(var_edges)]
    return result
