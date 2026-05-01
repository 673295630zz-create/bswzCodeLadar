from autosar_code_relation_analyzer.c_function_parser import parse_functions
from autosar_code_relation_analyzer.c_preprocessor import preprocess_code


def test_parse_normal_and_autosar_functions():
    code = '''
    static int Bar(int a) { return a; }
    FUNC(void, SPIIF_CODE) SpiIf_MainFunction(void)
    {
        Bar(1);
    }
    '''
    funcs = parse_functions('x.c', preprocess_code(code))
    names = {f.name for f in funcs}
    assert 'Bar' in names
    assert 'SpiIf_MainFunction' in names
