from __future__ import annotations

import argparse
from pathlib import Path

from .c_function_parser import parse_functions
from .c_preprocessor import preprocess_code
from .drawio_writer import write_drawio
from .markdown_writer import write_markdown_report
from .relation_analyzer import analyze_relations
from .source_scanner import scan_sources


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='AUTOSAR code relation analyzer')
    parser.add_argument('--src', required=True, help='Source directory. Recursively scans subfolders.')
    parser.add_argument('--output', required=True, help='Output draw.io file path.')
    parser.add_argument('--report', required=True, help='Output markdown report path.')
    parser.add_argument('--include-headers', action='store_true', default=True, help='Scan .h files (enabled by default).')
    parser.add_argument('--no-headers', action='store_true', help='Disable .h scanning and only analyze .c files.')
    parser.add_argument('--exclude', nargs='*', default=[], help='Exclude path keywords, e.g. Generated build output.')
    parser.add_argument('--variables', nargs='*', default=None, help='Variable whitelist.')
    parser.add_argument('--all-variables', action='store_true', help='Analyze all variable-like tokens instead of auto/global filter.')
    parser.add_argument('--all-functions', action='store_true', default=True, help='Analyze all parsed functions (default true).')
    parser.add_argument('--functions', nargs='*', default=None, help='Analyze only specific function names.')
    parser.add_argument('--entry', default=None, help='Entry function to highlight in report.')
    return parser


def main() -> None:
    args = build_parser().parse_args()
    include_headers = args.include_headers and not args.no_headers
    sources = scan_sources(args.src, include_headers=include_headers, exclude_keywords=args.exclude)
    if not sources:
        raise SystemExit('No source files found. Check --src / exclude filters / header switch.')

    functions = []
    for src in sources:
        processed = preprocess_code(src.content)
        functions.extend(parse_functions(str(src.path), processed))

    if args.functions:
        wanted = set(args.functions)
        functions = [fn for fn in functions if fn.name in wanted]

    result = analyze_relations(args.src, sources, functions, args.variables, analyze_all_variables=args.all_variables)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    write_drawio(result, args.output)
    write_markdown_report(result, args.report, args.entry)
    print(f'Analyzed files: {len(sources)}')
    print(f'Functions: {len(result.functions)} | Calls: {len(result.call_relations)} | Variable relations: {len(result.variable_relations)}')
    print(f'Generated: {args.output}')
    print(f'Generated: {args.report}')


if __name__ == '__main__':
    main()
