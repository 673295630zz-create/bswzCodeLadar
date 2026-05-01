from pathlib import Path

from autosar_code_relation_analyzer.models import AnalysisResult
from autosar_code_relation_analyzer.drawio_writer import write_drawio


def test_drawio_contains_mxfile(tmp_path: Path):
    result = AnalysisResult(source_root='.')
    output = tmp_path / 'x.drawio'
    write_drawio(result, str(output))
    content = output.read_text(encoding='utf-8')
    assert '<mxfile' in content
    assert 'Code Relation' in content
