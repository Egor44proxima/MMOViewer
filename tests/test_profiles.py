from mmo_viewer.core.parser import parse_mmo_bytes
from mmo_viewer.core.profiles import (
    LEGACY_V3,
    PRODUCTION_V3_UKTZED,
    ProfileStatus,
    detect_profile,
)


def _document() -> str:
    return "\t".join(
        [
            "INV",
            "29.09.2026",
            "0",
            "Supplier",
            "Bank",
            "26000000000000",
            "300000",
            "000",
            "Kyiv",
            "",
            "",
            "100.00",
            "107.00",
            "30.09.2026",
            "0",
            "1",
            "2",
        ]
    )


def _item(count: int, *, terminal_tab: bool = False, last_value: str = "3004900000") -> str:
    values = [f"F{i}" for i in range(1, count + 1)]
    if count >= 21:
        values[8] = "7"
        values[15] = "1"
        values[19] = "100.00"
        values[20] = "100.00"
    if count >= 22:
        values[21] = last_value
    text = "\t".join(values)
    return text + ("\t" if terminal_tab else "")


def _mmo(items: list[str], *, document: str | None = None):
    text = "\r\n".join(
        [
            "РАСХОДНАЯ_НАКЛАДНАЯ\t12345678\t87654321\tверсия_3",
            document or _document(),
            "comment",
            *items,
        ]
    ) + "\r\n"
    return parse_mmo_bytes(text.encode("cp1251"))


def test_detects_legacy_profile():
    match = detect_profile(_mmo([_item(21)]))
    assert match.status == ProfileStatus.SUPPORTED
    assert match.profile == LEGACY_V3


def test_detects_production_uktzed_profile():
    match = detect_profile(_mmo([_item(22, terminal_tab=True)]))
    assert match.status == ProfileStatus.SUPPORTED
    assert match.profile == PRODUCTION_V3_UKTZED
    assert match.profile.uktzed_field_index == 22


def test_22_physical_fields_with_empty_last_value_are_ambiguous():
    match = detect_profile(_mmo([_item(22, last_value="")]))
    assert match.status == ProfileStatus.AMBIGUOUS
    assert match.profile is None


def test_problematic_18_24_layout_is_unsupported():
    document = _document() + "\textra"
    match = detect_profile(_mmo([_item(23, terminal_tab=True)], document=document))
    assert match.status == ProfileStatus.UNSUPPORTED
    assert match.profile is None


def test_mixed_legacy_and_production_profiles_are_unsupported():
    match = detect_profile(_mmo([_item(21), _item(22, terminal_tab=True)]))
    assert match.status == ProfileStatus.UNSUPPORTED
    assert match.profile is None
