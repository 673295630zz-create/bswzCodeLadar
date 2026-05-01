from __future__ import annotations

from .models import AnalysisResult


def write_markdown_report(result: AnalysisResult, output_path: str, entry: str | None = None) -> None:
    lines: list[str] = ['# Code Relation Report', '', '## Summary']
    lines.extend([
        f'- Source root: {result.source_root}',
        f'- Number of source files: {len(result.source_files)}',
        f'- Number of functions: {len(result.functions)}',
        f'- Number of external functions: {len(result.external_functions)}',
        f'- Number of variables: {len(result.variables)}',
        f'- Number of call relations: {len(result.call_relations)}',
        f'- Number of variable relations: {len(result.variable_relations)}',
        '',
    ])
    if entry:
        lines.extend([f'- Highlight entry function: {entry}', ''])

    lines.extend(['## Function Call Relations', '', '| Caller | Callee | Callee Type | Caller File |', '|---|---|---|---|'])
    for rel in result.call_relations:
        ctype = 'external' if rel.target in result.external_functions else 'internal'
        lines.append(f'| {rel.source} | {rel.target} | {ctype} | {rel.file_path} |')

    lines.extend(['', '## Variable Processing Relations', '', '| Function | Variable | Relation | File | Line Hint |', '|---|---|---|---|---|'])
    for rel in result.variable_relations:
        lines.append(f'| {rel.source} | {rel.target} | {rel.relation_type} | {rel.file_path} | {rel.line_hint or ""} |')

    lines.extend(['', '## Functions', ''])
    for fn in sorted(result.functions, key=lambda x: x.name):
        lines.append(f'### {fn.name}')
        lines.append(f'- Defined in: {fn.file_path}:{fn.start_line}-{fn.end_line}')
        lines.append(f'- Calls: {", ".join(sorted({r.target for r in result.call_relations if r.source == fn.name})) or "-"}')
        for label, rtype in [('Reads', 'reads'), ('Writes', 'writes'), ('Read-Writes', 'read_writes'), ('Passed by Address', 'passed_by_address')]:
            targets = sorted({r.target for r in result.variable_relations if r.source == fn.name and r.relation_type == rtype})
            lines.append(f'- {label}: {", ".join(targets) if targets else "-"}')
        lines.append('')

    lines.extend([
        '## Notes',
        '- This is a lightweight static analyzer.',
        '- No full macro expansion.',
        '- No compile-time conditional branch selection.',
        '- No real function pointer binding.',
        '- No full type-system analysis.',
        '- Results are for code understanding and preliminary design analysis.',
    ])

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
