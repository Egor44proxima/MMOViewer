from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .models import MMOFile
from .spec import (
    DOCUMENT_FIELDS,
    HEADER_FIELDS,
    LEGACY_ITEM_FIELDS,
    PRODUCTION_ITEM_FIELDS,
)


class ProfileStatus(str, Enum):
    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"
    AMBIGUOUS = "ambiguous"


@dataclass(frozen=True, slots=True)
class FormatProfile:
    key: str
    label: str
    document_field_count: int
    item_fields: tuple
    allow_header_terminal_empty: bool = False
    allow_item_terminal_empty: bool = False
    uktzed_field_index: int | None = None  # 1-based
    morion_field_index: int | None = 5     # 1-based


@dataclass(frozen=True, slots=True)
class ProfileMatch:
    status: ProfileStatus
    profile: FormatProfile | None
    reason: str


LEGACY_V3 = FormatProfile(
    key="legacy_v3_17_21",
    label="Legacy v3 · 17/21",
    document_field_count=len(DOCUMENT_FIELDS),
    item_fields=LEGACY_ITEM_FIELDS,
    allow_header_terminal_empty=True,
    allow_item_terminal_empty=False,
)

PRODUCTION_V3_UKTZED = FormatProfile(
    key="production_v3_17_22_uktzed",
    label="Production v3 · 17/22 · UKTZED",
    document_field_count=len(DOCUMENT_FIELDS),
    item_fields=PRODUCTION_ITEM_FIELDS,
    allow_header_terminal_empty=True,
    allow_item_terminal_empty=True,
    uktzed_field_index=22,
)

SUPPORTED_PROFILES = (LEGACY_V3, PRODUCTION_V3_UKTZED)


def _header_supported(mmo: MMOFile) -> bool:
    if mmo.header is None:
        return False
    actual = len(mmo.header.fields)
    return actual == len(HEADER_FIELDS) or (
        actual == len(HEADER_FIELDS) + 1 and mmo.header.fields[-1] == ""
    )


def _item_shape(fields: list[str]) -> str | None:
    actual = len(fields)
    if actual == len(LEGACY_ITEM_FIELDS):
        return "legacy"
    if actual == len(PRODUCTION_ITEM_FIELDS):
        # 22 physical fields ending in empty are structurally ambiguous:
        # legacy 21 + terminal TAB OR production 22 with empty UKTZED.
        return "ambiguous" if fields[-1] == "" else "production"
    if actual == len(PRODUCTION_ITEM_FIELDS) + 1 and fields[-1] == "":
        return "production"
    return None


def detect_profile(mmo: MMOFile) -> ProfileMatch:
    if not _header_supported(mmo):
        return ProfileMatch(
            ProfileStatus.UNSUPPORTED,
            None,
            "HEADER does not match a confirmed structural shape.",
        )

    if mmo.document is None or len(mmo.document.fields) != len(DOCUMENT_FIELDS):
        return ProfileMatch(
            ProfileStatus.UNSUPPORTED,
            None,
            "DOCUMENT does not contain the confirmed 17 fields.",
        )

    if not mmo.items:
        # No detail rows means there is no evidence to select 21 vs 22.
        return ProfileMatch(
            ProfileStatus.AMBIGUOUS,
            None,
            "No ITEM rows are available to select a confirmed item profile.",
        )

    shapes = [_item_shape(item.fields) for item in mmo.items]
    if any(shape is None for shape in shapes):
        return ProfileMatch(
            ProfileStatus.UNSUPPORTED,
            None,
            "At least one ITEM row has an unsupported field count.",
        )

    strong = {shape for shape in shapes if shape in {"legacy", "production"}}
    if len(strong) > 1:
        return ProfileMatch(
            ProfileStatus.UNSUPPORTED,
            None,
            "The document mixes confirmed legacy and production ITEM layouts.",
        )

    if strong == {"legacy"}:
        return ProfileMatch(ProfileStatus.SUPPORTED, LEGACY_V3, "Matched legacy 17/21 profile.")

    if strong == {"production"}:
        return ProfileMatch(
            ProfileStatus.SUPPORTED,
            PRODUCTION_V3_UKTZED,
            "Matched production 17/22 UKTZED profile.",
        )

    return ProfileMatch(
        ProfileStatus.AMBIGUOUS,
        None,
        "ITEM rows are structurally valid but do not distinguish legacy 21+TAB from production 22 with empty UKTZED.",
    )
