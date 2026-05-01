from __future__ import annotations

import re
from collections import defaultdict

from .models import AnalysisResult, FunctionDef, RelationEdge, SourceFile

C_KEYWORDS = {'if', 'while', 'for', 'switch', 'return', 'sizeof', 'typedef', 'struct', 'union', 'enum'}
CALL_RE = re.compile(r'\b([A-Za-z_]\w*)\s*\(')
TOKEN_RE = re.compile(r'\b[A-Za-z_]\w*(?:->\w+|\.\w+)?\b')
ASSIGN_RE = re.compile(r'\b([A-Za-z_]\w*(?:->\w+|\.\w+)?)\s*=\s*([^;]+);')
RW_ASSIGN_RE = re.compile(r'\b([A-Za-z_]\w*(?:->\w+|\.\w+)?)\s*[+\-*/%&|^]=')
INC_RE = re.compile(r'(\+\+|--)\s*([A-Za-z_]\w*(?:->\w+|\.\w+)?)|([A-Za-z_]\w*(?:->\w+|\.\w+)?)\s*(\+\+|--)')
DEFINE_RE = re.compile(r'^\s*#\s*define\s+([A-Za-z_]\w+)')


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


def analyze_relations(source_root: str, sources: list[SourceFile], functions: list[FunctionDef], variables: list[str] | None, analyze_all_variables: bool = False) -> AnalysisResult:
    result = AnalysisResult(source_root=source_root, source_files=[str(s.path) for s in sources], functions=functions)
    defined = {f.name for f in functions}
    macro_names: set[str] = set()
    for s in sources:
        for m in DEFINE_RE.finditer(s.content):
            macro_names.add(m.group(1))

    variable_filter = None if analyze_all_variables else (set(variables) if variables else collect_candidate_globals([s.content for s in sources]))

    call_edges, cond_edges, def_edges, var_edges = set(), set(), set(), set()

    for fn in functions:
        lines = fn.body.splitlines()
        for call in CALL_RE.finditer(fn.body):
            callee = call.group(1)
            if callee in C_KEYWORDS or callee in macro_names:
                continue
            call_edges.add((fn.name, callee, 'calls', fn.file_path))
            if callee not in defined:
                result.external_functions.add(callee)

        for line_no, line in enumerate(lines, start=fn.start_line):
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith(('if', 'while', 'switch')):
                cond_edges.add((fn.name, f'COND@{fn.name}:{line_no}', 'if_condition', fn.file_path, line_no))
                for tok in TOKEN_RE.findall(stripped):
                    tok_n = _normalize_var(tok)
                    if variable_filter is None or tok_n in variable_filter or tok_n.split('.')[0] in variable_filter:
                        var_edges.add((fn.name, tok_n, 'reads', fn.file_path, line_no))
                        result.variables.add(tok_n)

            for macro in macro_names:
                if re.search(rf'\b{re.escape(macro)}\b', stripped):
                    def_edges.add((fn.name, macro, 'uses_define', fn.file_path, line_no))

            for m in RW_ASSIGN_RE.finditer(stripped):
                var = _normalize_var(m.group(1))
                if variable_filter is None or var in variable_filter or var.split('.')[0] in variable_filter:
                    var_edges.add((fn.name, var, 'read_writes', fn.file_path, line_no))
                    result.variables.add(var)
            for m in INC_RE.finditer(stripped):
                var = _normalize_var(m.group(2) or m.group(3))
                if variable_filter is None or var in variable_filter or var.split('.')[0] in variable_filter:
                    var_edges.add((fn.name, var, 'read_writes', fn.file_path, line_no))
                    result.variables.add(var)
            for m in ASSIGN_RE.finditer(stripped):
                lhs = _normalize_var(m.group(1))
                rhs = m.group(2)
                if variable_filter is None or lhs in variable_filter or lhs.split('.')[0] in variable_filter:
                    var_edges.add((fn.name, lhs, 'writes', fn.file_path, line_no))
                    result.variables.add(lhs)
                for tok in TOKEN_RE.findall(rhs):
                    tok_n = _normalize_var(tok)
                    if tok_n == lhs:
                        continue
                    if variable_filter is None or tok_n in variable_filter or tok_n.split('.')[0] in variable_filter:
                        var_edges.add((fn.name, tok_n, 'reads', fn.file_path, line_no))
                        result.variables.add(tok_n)
            for addr in re.findall(r'&\s*([A-Za-z_]\w*(?:->\w+|\.\w+)?)', stripped):
                var = _normalize_var(addr)
                if variable_filter is None or var in variable_filter or var.split('.')[0] in variable_filter:
                    var_edges.add((fn.name, var, 'passed_by_address', fn.file_path, line_no))
                    result.variables.add(var)

    result.call_relations = [RelationEdge(*e, line_hint=None) for e in sorted(call_edges)]
    result.condition_relations = [RelationEdge(*e) for e in sorted(cond_edges)]
    result.define_relations = [RelationEdge(*e) for e in sorted(def_edges)]
    result.variable_relations = [RelationEdge(*e) for e in sorted(var_edges)]
    return result
