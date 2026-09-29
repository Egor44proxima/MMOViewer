from mmo_viewer.core.item_projection import build_item_view_columns, item_column_value
from mmo_viewer.core.parser import parse_mmo_bytes


def _document(extra: str = "") -> str:
    base = [
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
    if extra:
        base.append(extra)
    return "\t".join(base)


def _item(count: int, *, terminal_tab: bool = False) -> str:
    values = [f"V{i}" for i in range(1, count + 1)]
    if count >= 21:
        values[1] = "Product"
        values[4] = "MORION-1"
        values[14] = "pack"
        values[15] = "1"
        values[19] = "100.00"
        values[20] = "100.00"
    if count >= 22:
        values[21] = "3004900000"
    text = "\t".join(values)
    return text + ("\t" if terminal_tab else "")


def _mmo(item: str, *, document: str | None = None):
    text = "\r\n".join(
        [
            "РАСХОДНАЯ_НАКЛАДНАЯ\t12345678\t87654321\tверсия_3",
            document or _document(),
            "comment",
            item,
        ]
    ) + "\r\n"
    return parse_mmo_bytes(text.encode("cp1251"))


def test_legacy_projection_contains_all_21_semantic_fields_once():
    mmo = _mmo(_item(21))
    columns = build_item_view_columns(mmo)

    indexes = [column.field_index for column in columns if column.field_index]
    assert set(indexes) == set(range(1, 22))
    assert len(indexes) == 21

    labels = [column.label for column in columns]
    assert labels[:7] == [
        "Morion ID",
        "УКТ ЗЕД",
        "Товар",
        "Од.",
        "К-сть",
        "Ціна",
        "Сума",
    ]
    assert item_column_value(mmo.items[0].fields, columns[0]) == "MORION-1"
    assert item_column_value(mmo.items[0].fields, columns[1]) == "—"


def test_production_projection_contains_all_22_semantic_fields_once():
    mmo = _mmo(_item(22, terminal_tab=True))
    columns = build_item_view_columns(mmo)

    indexes = [column.field_index for column in columns if column.field_index]
    assert set(indexes) == set(range(1, 23))
    assert len(indexes) == 22
    assert item_column_value(mmo.items[0].fields, columns[1]) == "3004900000"

    # The physical terminal TAB is evidence, not a semantic field column.
    assert not [column for column in columns if column.field_index == 23]


def test_unsupported_layout_exposes_all_physical_fields_only_as_raw():
    mmo = _mmo(_item(23, terminal_tab=True), document=_document("extra"))
    columns = build_item_view_columns(mmo)

    assert [column.field_index for column in columns[:7]] == [None] * 7
    raw_columns = [column for column in columns if not column.semantic]
    assert {column.field_index for column in raw_columns} == set(range(1, 25))
    assert raw_columns[-1].label == "F24 · RAW"
    assert item_column_value(mmo.items[0].fields, raw_columns[-1]) == ""
