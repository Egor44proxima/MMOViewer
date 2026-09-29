from pathlib import Path

from mmo_viewer.core.parser import parse_mmo_bytes
from mmo_viewer.core.validator import open_and_validate, validate_mmo

FIXTURES = Path(__file__).parent / "fixtures"


def codes(result):
    return {d.code for d in result.diagnostics}


def _production_v3_bytes(*, gross: str = "107.00", extra_tail: str = "") -> bytes:
    header = "РАСХОДНАЯ_НАКЛАДНАЯ\t12345678\t87654321\tверсия_3\t"
    document = (
        "INV-UKT\t29.09.2026\t0\tТестовий постачальник\t"
        "АКЦІОНЕРНЕ ТОВАРИСТВО ТЕСТОВИЙ МІЖНАРОДНИЙ БАНК ДОВГА НАЗВА\t"
        "UA263348510000000002600590803\t334851\t(044) 000-00-00\t"
        "Київ\tLIC-1\t29.09.2027\t100.00\t"
        + gross
        + "\t30.09.2026\t0\t1\t2"
    )
    comment = "Synthetic production v3 fixture"
    item_fields = [
        "1",
        "Тестовий товар",
        "M1",
        "Тестовий виробник",
        "123456",
        "UA/TEST",
        "29.09.2026",
        "01.01.2099",
        "7",
        " ",
        "SER-1",
        "CERT-1",
        "29.09.2026",
        "29.09.2028",
        "паков",
        "1",
        "100.00",
        "90.00",
        "0",
        "100.00",
        "100.00",
        "3004900000",
    ]
    item = "\t".join(item_fields) + "\t" + extra_tail
    text = "\r\n".join([header, document, comment, item]) + "\r\n"
    return text.encode("cp1251")


def test_valid_minimal_has_no_errors():
    result = open_and_validate(FIXTURES / "valid_minimal.mmo")
    assert result.status == "VALID"
    assert not result.errors


def test_single_terminal_tabs_are_accepted():
    result = open_and_validate(FIXTURES / "invalid_trailing_tabs.mmo")
    assert "MMO_HEADER_FIELD_COUNT" not in codes(result)
    assert "MMO_ITEM_FIELD_COUNT" not in codes(result)


def test_invalid_item_total_is_detected():
    result = open_and_validate(FIXTURES / "invalid_total.mmo")
    assert "MMO_ITEM_TOTAL_MISMATCH" in codes(result)


def test_production_v3_uktzed_and_vat_projection_have_no_errors():
    mmo = parse_mmo_bytes(_production_v3_bytes())
    result = validate_mmo(mmo)

    assert not result.errors
    assert "MMO_HEADER_FIELD_COUNT" not in codes(result)
    assert "MMO_ITEM_FIELD_COUNT" not in codes(result)
    assert "MMO_INVALID_NUMBER" not in codes(result)
    assert "MMO_DOCUMENT_NET_TOTAL_MISMATCH" not in codes(result)
    assert "MMO_DOCUMENT_GROSS_TOTAL_MISMATCH" not in codes(result)
    assert mmo.items[0].fields[21] == "3004900000"


def test_legacy_width_limits_are_advisory_warnings():
    result = validate_mmo(parse_mmo_bytes(_production_v3_bytes()))

    width_diags = [d for d in result.warnings if d.code == "MMO_FIELD_WIDTH_LEGACY"]
    assert width_diags
    assert not [d for d in result.errors if d.code == "MMO_FIELD_WIDTH_LEGACY"]


def test_whitespace_only_numeric_field_is_treated_as_empty():
    result = validate_mmo(parse_mmo_bytes(_production_v3_bytes()))
    assert "MMO_INVALID_NUMBER" not in codes(result)


def test_production_gross_total_mismatch_is_detected():
    result = validate_mmo(parse_mmo_bytes(_production_v3_bytes(gross="108.00")))
    assert "MMO_DOCUMENT_GROSS_TOTAL_MISMATCH" in codes(result)


def test_more_than_one_extra_terminal_field_is_structural_error():
    result = validate_mmo(parse_mmo_bytes(_production_v3_bytes(extra_tail="\t")))
    assert "MMO_ITEM_FIELD_COUNT" in codes(result)
