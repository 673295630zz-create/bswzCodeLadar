# autosar_code_relation_analyzer

## Tool Purpose
A lightweight static code relation analyzer for embedded C / AUTOSAR BSW projects. It extracts function call relations and variable processing relations.

## Installation
```bash
cd autosar_code_relation_analyzer
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## CLI Example
```bash
python -m autosar_code_relation_analyzer.cli \
  --src ./examples/spi_demo/src \
  --output ./example.drawio \
  --report ./example_report.md \
  --include-headers
```

## Output Files
- `.drawio`: diagrams.net compatible XML graph with function/external/variable nodes.
- `.md`: human-readable report with summary, relation tables, and per-function details.

## Suitable Scenarios
- Fast architecture/code understanding.
- AUTOSAR BSW module relationship review.
- Preliminary impact analysis and design discussion.

## Unsuitable Scenarios
- Compiler-grade semantic correctness.
- Exact function pointer binding.
- Full preprocessor and conditional compilation simulation.

## AUTOSAR BSW Usage Suggestions
- Use `--include-headers` to capture declarations and inline utilities.
- Use `--exclude Generated build output` to skip generated trees.
- Use `--variables` for focused analysis in large projects.
