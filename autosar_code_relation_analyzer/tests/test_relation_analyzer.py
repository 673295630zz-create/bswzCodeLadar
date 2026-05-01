from pathlib import Path

from autosar_code_relation_analyzer.c_function_parser import parse_functions
from autosar_code_relation_analyzer.c_preprocessor import preprocess_code
from autosar_code_relation_analyzer.models import SourceFile
from autosar_code_relation_analyzer.relation_analyzer import analyze_relations


def test_call_and_variable_relations():
    code = '''
    int g_State;
    void B(void) {}
    void A(void) {
        g_State = 1;
        if (g_State == 1) { B(); }
        g_State++;
    }
    '''
    sf = SourceFile(path=Path('a.c'), content=code)
    funcs = parse_functions('a.c', preprocess_code(code))
    result = analyze_relations('.', [sf], funcs, ['g_State'])
    call_targets = {r.target for r in result.call_relations if r.source == 'A'}
    assert 'B' in call_targets
    rels = {(r.target, r.relation_type) for r in result.variable_relations if r.source == 'A'}
    assert ('g_State', 'writes') in rels
    assert ('g_State', 'reads') in rels
    assert ('g_State', 'read_writes') in rels
