from pathlib import Path

from autosar_code_relation_analyzer.c_function_parser import parse_functions
from autosar_code_relation_analyzer.c_preprocessor import preprocess_code


def test_specific_function_filter_logic():
    code = """
    void A(void){}
    void B(void){}
    """
    funcs = parse_functions('x.c', preprocess_code(code))
    filtered = [f for f in funcs if f.name in {'B'}]
    assert len(filtered) == 1
    assert filtered[0].name == 'B'
