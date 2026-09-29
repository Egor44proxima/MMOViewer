from __future__ import annotations

from dataclasses import dataclass

from .models import MMOFile
from .profiles import ProfileStatus, detect_profile
from .spec import LEGACY_ITEM_FIELDS


@dataclass(frozen=True, slots=True)
class ItemViewColumn:
    key: str
    label: str
    field_index: int | None = None  # 1-based physical field index
    semantic: bool = True


def build_item_view_columns(mmo: MMOFile) -> tuple[ItemViewColumn, ...]:
    """Build a profile-aware, lossless Items-table projection.

    Confirmed/ambiguous layouts expose only semantics that are safe to name.
    Unsupported layouts expose all physical fields as generic RAW columns so
    the UI never invents business meaning for unknown positions.
    """
    match = detect_profile(mmo)
    semantic_allowed = match.status != ProfileStatus.UNSUPPORTED

    if match.status == ProfileStatus.SUPPORTED and match.profile is not None:
        semantic_specs = match.profile.item_fields
        uktzed_index = match.profile.uktzed_field_index
    elif match.status == ProfileStatus.AMBIGUOUS:
        # Only the shared legacy 1..21 semantics are safe in an ambiguous row.
        semantic_specs = LEGACY_ITEM_FIELDS
        uktzed_index = None
    else:
        semantic_specs = ()
        uktzed_index = None

    core = (
        ItemViewColumn(
            "morion",
            "Morion ID",
            5 if semantic_allowed and len(semantic_specs) >= 5 else None,
        ),
        ItemViewColumn("uktzed", "УКТ ЗЕД", uktzed_index),
        ItemViewColumn(
            "product",
            "Товар",
            2 if semantic_allowed and len(semantic_specs) >= 2 else None,
        ),
        ItemViewColumn(
            "unit",
            "Од.",
            15 if semantic_allowed and len(semantic_specs) >= 15 else None,
        ),
        ItemViewColumn(
            "qty",
            "К-сть",
            16 if semantic_allowed and len(semantic_specs) >= 16 else None,
        ),
        ItemViewColumn(
            "price",
            "Ціна",
            20 if semantic_allowed and len(semantic_specs) >= 20 else None,
        ),
        ItemViewColumn(
            "total",
            "Сума",
            21 if semantic_allowed and len(semantic_specs) >= 21 else None,
        ),
    )

    columns = list(core)
    represented = {
        column.field_index
        for column in columns
        if column.field_index is not None
    }

    for index, spec in enumerate(semantic_specs, start=1):
        if index in represented:
            continue
        columns.append(
            ItemViewColumn(
                key=f"field_{index}",
                label=f"F{index:02d} · {spec.name}",
                field_index=index,
                semantic=True,
            )
        )
        represented.add(index)

    max_physical = max((len(item.fields) for item in mmo.items), default=0)

    # For a supported profile, terminal TAB evidence remains in RAW and is not
    # promoted to a semantic table column. Ambiguous/unsupported layouts expose
    # unclassified physical fields generically instead.
    if match.status != ProfileStatus.SUPPORTED:
        for index in range(1, max_physical + 1):
            if index in represented:
                continue
            columns.append(
                ItemViewColumn(
                    key=f"raw_{index}",
                    label=f"F{index:02d} · RAW",
                    field_index=index,
                    semantic=False,
                )
            )
            represented.add(index)

    return tuple(columns)


def item_column_value(fields: list[str], column: ItemViewColumn) -> str:
    if column.field_index is None:
        return "—"
    index = column.field_index - 1
    if index >= len(fields):
        return ""
    return fields[index]
