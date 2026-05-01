from pathlib import Path

from autosar_code_relation_analyzer.source_scanner import scan_sources


def test_recursive_scan_c_and_h(tmp_path: Path):
    sub = tmp_path / 'a' / 'b'
    sub.mkdir(parents=True)
    (sub / 'x.c').write_text('void A(void){}', encoding='utf-8')
    (sub / 'x.h').write_text('void A(void);', encoding='utf-8')

    files = scan_sources(str(tmp_path))
    names = {f.path.name for f in files}
    assert 'x.c' in names
    assert 'x.h' in names
