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

## Script Entry (Recommended for Large Projects)
Use the script file to trigger analysis directly:
```bash
python run_analyzer.py \
  --src ./your_project_root \
  --output ./code_relation.drawio \
  --report ./code_relation_report.md
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
- Large source trees where recursive subfolder scanning is required.

## Unsuitable Scenarios
- Compiler-grade semantic correctness.
- Exact function pointer binding.
- Full preprocessor and conditional compilation simulation.

## AUTOSAR BSW Usage Suggestions
- By default, the tool recursively scans all subfolders and includes both `.c` and `.h` files.
- Use `--no-headers` to limit scanning to `.c` for very large repositories.
- Use `--exclude Generated build output` to skip generated trees.
- Use `--variables` for focused analysis in large projects.
