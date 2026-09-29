from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


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

COMMENT_FIELDS = (
    FieldSpec("Коментар", FieldType.STRING, 200),
)

LEGACY_ITEM_FIELD_COUNT = 21

ITEM_FIELDS = (
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
    FieldSpec(
        "Код УКТ ЗЕД",
        FieldType.STRING,
        None,
        hint="Production v3 extension: field 22. Maximum width is not yet established.",
    ),
)

PRODUCTION_ITEM_FIELD_COUNT = len(ITEM_FIELDS)

EXPECTED_SIGNATURE = "РАСХОДНАЯ_НАКЛАДНАЯ"
EXPECTED_VERSION = "версия_3"
EXPECTED_ENCODING = "cp1251"
