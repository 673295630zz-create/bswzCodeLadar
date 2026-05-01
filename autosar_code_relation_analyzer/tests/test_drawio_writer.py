from pathlib import Path

from autosar_code_relation_analyzer.drawio_writer import write_drawio
from autosar_code_relation_analyzer.models import AnalysisResult, FunctionDef, RelationEdge


def test_drawio_contains_mxfile(tmp_path: Path):
    result = AnalysisResult(source_root='.')
    result.functions = [FunctionDef(name='A', file_path='a.c', start_line=1, end_line=2, body='B();'), FunctionDef(name='B', file_path='a.c', start_line=3, end_line=4, body='')]
    result.call_relations = [RelationEdge('A', 'B', 'calls', 'a.c')]
    output = tmp_path / 'x.drawio'
    write_drawio(result, str(output))
    content = output.read_text(encoding='utf-8')
    assert '<mxfile' in content
    assert 'Code Relation' in content
    assert 'orthogonalEdgeStyle' in content
