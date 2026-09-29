from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence


class FieldType(str, Enum):
    STRING = "string"
    DATE = "date"
    NUMBER = "number"


@dataclass(frozen=True, slots=True)
class FieldSpec:
    name: str
    field_type: FieldType
    width: int | None
    decimals: int = 0
    hint: str = ""


HEADER_FIELDS = (
    FieldSpec("Тип документа", FieldType.STRING, 19),
    FieldSpec("ЄДРПОУ постачальника", FieldType.STRING, 10),
    FieldSpec("ЄДРПОУ аптеки-отримувача", FieldType.STRING, 10),
    FieldSpec("Версія файлу", FieldType.STRING, 10),
)

DOCUMENT_FIELDS = (
    FieldSpec("Номер документа", FieldType.STRING, 25),
    FieldSpec("Дата документа", FieldType.DATE, 10),
    FieldSpec("Номер податкової накладної", FieldType.STRING, 25),
    FieldSpec("Найменування постачальника", FieldType.STRING, 50),
    FieldSpec("Банк", FieldType.STRING, 50),
    FieldSpec("Р/р", FieldType.STRING, 25),
    FieldSpec("МФО", FieldType.STRING, 10),
    FieldSpec("Телефони", FieldType.STRING, 30),
    FieldSpec("Адреса постачальника", FieldType.STRING, 100),
    FieldSpec("Номер ліцензії", FieldType.STRING, 25),
    FieldSpec("Строк ліцензії", FieldType.DATE, 10),
    FieldSpec("Сума без ПДВ", FieldType.NUMBER, 15, 2),
    FieldSpec("Сума з ПДВ", FieldType.NUMBER, 15, 2),
    FieldSpec("Строк оплати", FieldType.DATE, 10),
    FieldSpec("Ціна включає ПДВ", FieldType.NUMBER, 1, 0, "Допустимі значення: 0 або 1"),
    FieldSpec("Код методу синхронізації", FieldType.NUMBER, 2, 0, "1=товар; 2=товар+виробник; 3=Morion"),
    FieldSpec("Знаків дробової частини суми", FieldType.NUMBER, 1, 0, "Допустимі значення: 2, 3 або 4"),
)

EXTENDED_DOCUMENT_FIELDS = DOCUMENT_FIELDS + (
    FieldSpec(
        "Договір / підстава",
        FieldType.STRING,
        None,
        hint="Observed production extension: document field 18. Exact vendor-independent width is not established.",
    ),
)

COMMENT_FIELDS = (
    FieldSpec("Коментар", FieldType.STRING, 200),
)

LEGACY_ITEM_FIELDS = (
    FieldSpec("ID товару", FieldType.STRING, 20),
    FieldSpec("Найменування товару", FieldType.STRING, 100),
    FieldSpec("ID виробника", FieldType.STRING, 20),
    FieldSpec("Найменування виробника", FieldType.STRING, 50),
    FieldSpec("ID зовнішній (наприклад Morion)", FieldType.STRING, 20, hint="Код має бути унікальним для методу синхронізації 3"),
    FieldSpec("Номер реєстрації", FieldType.STRING, 40),
    FieldSpec("Дата реєстрації", FieldType.DATE, 10),
    FieldSpec("Строк реєстрації", FieldType.DATE, 10),
    FieldSpec("Відсоток ПДВ", FieldType.NUMBER, 3, 0),
    FieldSpec("Макс. відсоток від митної ціни", FieldType.NUMBER, 3, 0),
    FieldSpec("№ серії", FieldType.STRING, 16),
    FieldSpec("Номер сертифіката", FieldType.STRING, 20),
    FieldSpec("Дата сертифіката", FieldType.DATE, 10),
    FieldSpec("Строк придатності", FieldType.DATE, 10),
    FieldSpec("Од. вим.", FieldType.STRING, 5),
    FieldSpec("Кількість", FieldType.NUMBER, 15, 3),
    FieldSpec("Ціна складська", FieldType.NUMBER, 16, 4),
    FieldSpec("Ціна митна", FieldType.NUMBER, 16, 4),
    FieldSpec("% націнки постачальника", FieldType.NUMBER, 6, 2),
    FieldSpec("Ціна відпускна", FieldType.NUMBER, 16, 4),
    FieldSpec("Сума відпускна", FieldType.NUMBER, 16, 4),
)

PRODUCTION_ITEM_FIELDS = LEGACY_ITEM_FIELDS + (
    FieldSpec(
        "Код УКТ ЗЕД",
        FieldType.STRING,
        None,
        hint="Observed production v3 extension: field 22.",
    ),
)

EXTENDED_ITEM_FIELDS = (
    *LEGACY_ITEM_FIELDS[:4],
    FieldSpec(
        "GTIN / штрихкод",
        FieldType.STRING,
        20,
        hint="Observed extended production v3 semantics for field 5.",
    ),
    *LEGACY_ITEM_FIELDS[5:],
    FieldSpec(
        "Код Моріон",
        FieldType.STRING,
        None,
        hint="Observed extended production v3 field 22; synchronization method 3 binds here.",
    ),
    FieldSpec(
        "Код УКТ ЗЕД",
        FieldType.STRING,
        None,
        hint="Observed extended production v3 field 23.",
    ),
)

# Backwards-compatible alias used by existing UI/imports.
ITEM_FIELDS = PRODUCTION_ITEM_FIELDS

LEGACY_ITEM_FIELD_COUNT = len(LEGACY_ITEM_FIELDS)
PRODUCTION_ITEM_FIELD_COUNT = len(PRODUCTION_ITEM_FIELDS)
EXTENDED_ITEM_FIELD_COUNT = len(EXTENDED_ITEM_FIELDS)
LEGACY_DOCUMENT_FIELD_COUNT = len(DOCUMENT_FIELDS)
EXTENDED_DOCUMENT_FIELD_COUNT = len(EXTENDED_DOCUMENT_FIELDS)


def has_single_terminal_empty(fields: Sequence[str], semantic_count: int) -> bool:
    return len(fields) == semantic_count + 1 and fields[-1] == ""


def is_extended_document(fields: Sequence[str]) -> bool:
    return len(fields) == EXTENDED_DOCUMENT_FIELD_COUNT


def document_specs_for(fields: Sequence[str]) -> tuple[FieldSpec, ...]:
    if is_extended_document(fields):
        return EXTENDED_DOCUMENT_FIELDS
    return DOCUMENT_FIELDS


def item_specs_for(fields: Sequence[str], *, extended_document: bool) -> tuple[FieldSpec, ...] | None:
    if extended_document:
        if len(fields) == EXTENDED_ITEM_FIELD_COUNT:
            return EXTENDED_ITEM_FIELDS
        if has_single_terminal_empty(fields, EXTENDED_ITEM_FIELD_COUNT):
            return EXTENDED_ITEM_FIELDS
        return None

    if len(fields) == LEGACY_ITEM_FIELD_COUNT:
        return LEGACY_ITEM_FIELDS
    if has_single_terminal_empty(fields, LEGACY_ITEM_FIELD_COUNT):
        return LEGACY_ITEM_FIELDS
    if len(fields) == PRODUCTION_ITEM_FIELD_COUNT:
        return PRODUCTION_ITEM_FIELDS
    if has_single_terminal_empty(fields, PRODUCTION_ITEM_FIELD_COUNT):
        return PRODUCTION_ITEM_FIELDS
    return None


def item_morion_field_index(fields: Sequence[str], *, extended_document: bool) -> int:
    return 22 if extended_document else 5


def item_uktzed_field_index(fields: Sequence[str], *, extended_document: bool) -> int | None:
    if extended_document:
        return 23
    specs = item_specs_for(fields, extended_document=False)
    if specs is PRODUCTION_ITEM_FIELDS:
        return 22
    return None


def item_gtin_field_index(fields: Sequence[str], *, extended_document: bool) -> int | None:
    return 5 if extended_document else None


EXPECTED_SIGNATURE = "РАСХОДНАЯ_НАКЛАДНАЯ"
EXPECTED_VERSION = "версия_3"
EXPECTED_ENCODING = "cp1251"
