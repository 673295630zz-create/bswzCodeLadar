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
    parser.add_argument('--src', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--report', required=True)
    parser.add_argument('--include-headers', action='store_true')
    parser.add_argument('--exclude', nargs='*', default=[])
    parser.add_argument('--variables', nargs='*', default=None)
    parser.add_argument('--entry', default=None)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    sources = scan_sources(args.src, args.include_headers, args.exclude)
    if not sources:
        raise SystemExit('No source files found. Check --src and --include-headers.')

    functions = []
    for src in sources:
        processed = preprocess_code(src.content)
        functions.extend(parse_functions(str(src.path), processed))

    result = analyze_relations(args.src, sources, functions, args.variables)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    write_drawio(result, args.output)
    write_markdown_report(result, args.report, args.entry)
    print(f'Generated: {args.output}')
    print(f'Generated: {args.report}')


if __name__ == '__main__':
    main()
