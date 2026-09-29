from pathlib import Path

from mmo_viewer.core.parser import parse_mmo, parse_mmo_bytes


def test_parser_preserves_trailing_tabs():
    data = "РАСХОДНАЯ_НАКЛАДНАЯ\tA\tB\tверсия_3\t\r\n".encode("cp1251")
    mmo = parse_mmo_bytes(data)
    assert mmo.header is not None
    assert len(mmo.header.fields) == 5
    assert mmo.header.fields[-1] == ""


def test_synthetic_valid_fixture_parses():
    path = Path(__file__).parent / "fixtures" / "valid_minimal.mmo"
    mmo = parse_mmo(path)
    assert mmo.encoding == "cp1251"
    assert mmo.eol == "CRLF"
    assert mmo.header and len(mmo.header.fields) == 4
    assert mmo.document and len(mmo.document.fields) == 17
    assert len(mmo.items) == 1
    assert len(mmo.items[0].fields) == 21
