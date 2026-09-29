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


def _extended_production_v3_bytes(*, gross: str = "0.11", duplicate_morion: bool = False) -> bytes:
    header = "РАСХОДНАЯ_НАКЛАДНАЯ\t31816235\t2989010104\tверсия_3"
    document = (
        "11-U-TEST\t28.09.2026\t1904510\tТестовий постачальник\tТестовий банк\t"
        "26002146146001\t305299\t(056) 000-00-00\tДніпро\t\t\t"
        "0.10\t"
        + gross
        + "\t02.10.2026\t0\t3\t2\tДоговір поставки №1 від 18.01.24"
    )
    comment = "Synthetic extended production v3 fixture"

    def item(gtin: str, morion: str, uktzed: str) -> str:
        fields = [
            "203.0128",
            "Тестовий товар",
            "4637",
            "Тестовий виробник",
            gtin,
            "UA/TEST/01/01",
            "21.02.2017",
            "01.01.2099",
            "7",
            "",
            "SER-1",
            "CERT-1",
            "12.08.2026",
            "01.06.2029",
            "пак",
            "1",
            "",
            "0.05",
            "",
            "0.05",
            "0.05",
            morion,
            uktzed,
        ]
        return "\t".join(fields) + "\t"

    second_morion = "99494" if duplicate_morion else "876751"
    text = "\r\n".join(
        [
            header,
            document,
            comment,
            item("4820011183242", "99494", "3004900000"),
            item("4823002247336", second_morion, "3004"),
        ]
    ) + "\r\n"
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


def test_extended_18_23_profile_is_accepted_and_identifiers_are_mapped():
    mmo = parse_mmo_bytes(_extended_production_v3_bytes())
    result = validate_mmo(mmo)

    assert not result.errors
    assert "MMO_PROFILE_EXTENDED_18_23" in codes(result)
    assert "MMO_DOCUMENT_FIELD_COUNT" not in codes(result)
    assert "MMO_ITEM_FIELD_COUNT" not in codes(result)
    assert "MMO_MORION_ID_MISSING" not in codes(result)
    assert "MMO_DOCUMENT_NET_TOTAL_MISMATCH" not in codes(result)
    assert "MMO_DOCUMENT_GROSS_TOTAL_MISMATCH" not in codes(result)

    assert mmo.document is not None
    assert mmo.document.fields[17] == "Договір поставки №1 від 18.01.24"
    assert len(mmo.items[0].fields) == 24
    assert mmo.items[0].fields[4] == "4820011183242"
    assert mmo.items[0].fields[21] == "99494"
    assert mmo.items[0].fields[22] == "3004900000"
    assert mmo.items[0].fields[23] == ""


def test_extended_profile_uses_document_level_vat_rounding():
    result = validate_mmo(parse_mmo_bytes(_extended_production_v3_bytes(gross="0.11")))
    assert "MMO_DOCUMENT_GROSS_TOTAL_MISMATCH" not in codes(result)

    bad = validate_mmo(parse_mmo_bytes(_extended_production_v3_bytes(gross="0.10")))
    assert "MMO_DOCUMENT_GROSS_TOTAL_MISMATCH" in codes(bad)


def test_extended_profile_morion_binding_is_field_22_not_gtin_field_5():
    result = validate_mmo(
        parse_mmo_bytes(_extended_production_v3_bytes(duplicate_morion=True))
    )
    duplicates = [
        d for d in result.errors if d.code == "MMO_MORION_ID_DUPLICATE"
    ]
    assert len(duplicates) == 1
    assert duplicates[0].field_index == 22
    assert duplicates[0].value == "99494"
