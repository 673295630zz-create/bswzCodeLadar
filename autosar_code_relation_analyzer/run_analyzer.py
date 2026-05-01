#!/usr/bin/env python3
"""Script entrypoint for large AUTOSAR/BSW projects.

Example:
python run_analyzer.py --src /path/to/project --output ./code_relation.drawio --report ./code_relation.md
"""

from autosar_code_relation_analyzer.cli import main


if __name__ == '__main__':
    main()
