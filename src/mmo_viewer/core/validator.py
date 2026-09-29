from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

from .models import Diagnostic, MMOFile, ParsedLine, Severity, ValidationResult
from .parser import parse_mmo
from .spec import (
    COMMENT_FIELDS,
    DOCUMENT_FIELDS,
    EXPECTED_ENCODING,
    EXPECTED_SIGNATURE,
    EXPECTED_VERSION,
    HEADER_FIELDS,
    ITEM_FIELDS,
    FieldSpec,
    FieldType,
)


def parse_decimal(value: str) -> Decimal | None:
    value = value.strip()
    if not value:
        return None
    normalized = value.replace(" ", "").replace(",", ".")
    try:
        return Decimal(normalized)
    except InvalidOperation:
        return None


def _decimal_places(value: str) -> int:
    value = value.strip().replace(",", ".")
    if "." not in value:
        return 0
    return len(value.rsplit(".", 1)[1])


def _valid_date(value: str) -> bool:
    if not value.strip():
        return True
    for fmt in ("%d.%m.%Y", "%d.%m.%y"):
        try:
            datetime.strptime(value.strip(), fmt)
            return True
        except ValueError:
            pass
    return False


def _add(diags: list[Diagnostic], severity: Severity, code: str, message: str, *,
         line: int | None = None, section: str = "", item_index: int | None = None,
         field_index: int | None = None, field_name: str = "", value: str = "") -> None:
    diags.append(Diagnostic(severity, code, message, line, section, item_index, field_index, field_name, value))


def _validate_field_count(diags: list[Diagnostic], parsed: ParsedLine | None, expected: int,
                          section: str, code: str, *, item_index: int | None = None) -> bool:
    if parsed is None:
        _add(diags, Severity.ERROR, code, f"Секція {section} відсутня; очікується {expected} полів.",
             section=section, item_index=item_index)
        return False
    actual = len(parsed.fields)
    if actual != expected:
        _add(diags, Severity.ERROR, code, f"Очікується {expected} полів, отримано {actual}.",
             line=parsed.line_no, section=section, item_index=item_index, value=str(actual))
        return False
    return True


def _validate_fields(diags: list[Diagnostic], parsed: ParsedLine, specs: tuple[FieldSpec, ...],
                     section: str, *, item_index: int | None = None) -> None:
    for idx, spec in enumerate(specs, start=1):
        if idx > len(parsed.fields):
            break
        value = parsed.fields[idx - 1]
        if len(value) > spec.width:
            _add(diags, Severity.ERROR, "MMO_FIELD_WIDTH",
                 f"Довжина поля {len(value)} перевищує максимум {spec.width}.",
                 line=parsed.line_no, section=section, item_index=item_index,
                 field_index=idx, field_name=spec.name, value=value)

        if not value:
            continue

        if spec.field_type == FieldType.DATE and not _valid_date(value):
            _add(diags, Severity.ERROR, "MMO_INVALID_DATE",
                 "Очікується дата DD.MM.YYYY або DD.MM.YY.",
                 line=parsed.line_no, section=section, item_index=item_index,
                 field_index=idx, field_name=spec.name, value=value)

        if spec.field_type == FieldType.NUMBER:
            number = parse_decimal(value)
            if number is None:
                _add(diags, Severity.ERROR, "MMO_INVALID_NUMBER", "Значення не є числом.",
                     line=parsed.line_no, section=section, item_index=item_index,
                     field_index=idx, field_name=spec.name, value=value)
            elif _decimal_places(value) > spec.decimals:
                _add(diags, Severity.ERROR, "MMO_DECIMAL_SCALE",
                     f"Допускається не більше {spec.decimals} знаків після роздільника.",
                     line=parsed.line_no, section=section, item_index=item_index,
                     field_index=idx, field_name=spec.name, value=value)


def validate_mmo(mmo: MMOFile) -> ValidationResult:
    diags: list[Diagnostic] = []

    _add(diags, Severity.INFO, "MMO_FILE_INFO",
         f"Кодування: {mmo.encoding}; EOL: {mmo.eol}; позицій: {mmo.item_count}.")

    if mmo.encoding != EXPECTED_ENCODING:
        _add(diags, Severity.WARNING, "MMO_ENCODING_NONSTANDARD",
             f"Очікуване кодування Windows-1251 (cp1251), файл прочитано як {mmo.encoding}.")
    if mmo.bom:
        _add(diags, Severity.WARNING, "MMO_BOM_PRESENT", "У файлі присутній BOM; legacy-приклади його не використовують.")
    if mmo.eol != "CRLF":
        _add(diags, Severity.WARNING, "MMO_EOL_NONSTANDARD",
             f"Очікується CRLF, фактично: {mmo.eol}.")

    header_ok = _validate_field_count(diags, mmo.header, len(HEADER_FIELDS), "HEADER", "MMO_HEADER_FIELD_COUNT")
    doc_ok = _validate_field_count(diags, mmo.document, len(DOCUMENT_FIELDS), "DOCUMENT", "MMO_DOCUMENT_FIELD_COUNT")
    comment_ok = _validate_field_count(diags, mmo.comment, len(COMMENT_FIELDS), "COMMENT", "MMO_COMMENT_FIELD_COUNT")

    if mmo.header:
        _validate_fields(diags, mmo.header, HEADER_FIELDS, "HEADER")
        if mmo.header.fields:
            if mmo.header.fields[0] != EXPECTED_SIGNATURE:
                _add(diags, Severity.ERROR, "MMO_INVALID_SIGNATURE",
                     f"Очікується '{EXPECTED_SIGNATURE}'.", line=mmo.header.line_no,
                     section="HEADER", field_index=1, field_name=HEADER_FIELDS[0].name,
                     value=mmo.header.fields[0])
        if len(mmo.header.fields) >= 4 and mmo.header.fields[3] != EXPECTED_VERSION:
            _add(diags, Severity.ERROR, "MMO_UNSUPPORTED_VERSION",
                 f"Очікується '{EXPECTED_VERSION}'.", line=mmo.header.line_no,
                 section="HEADER", field_index=4, field_name=HEADER_FIELDS[3].name,
                 value=mmo.header.fields[3])
        for idx in (2, 3):
            if len(mmo.header.fields) >= idx and not mmo.header.fields[idx - 1].strip():
                _add(diags, Severity.WARNING, "MMO_EDRPOU_MISSING", "ЄДРПОУ не вказано.",
                     line=mmo.header.line_no, section="HEADER", field_index=idx,
                     field_name=HEADER_FIELDS[idx - 1].name)

    if mmo.document:
        _validate_fields(diags, mmo.document, DOCUMENT_FIELDS, "DOCUMENT")
        fields = mmo.document.fields
        if len(fields) >= 15 and fields[14] and fields[14] not in {"0", "1"}:
            _add(diags, Severity.ERROR, "MMO_VAT_FLAG_INVALID", "Допустимі значення: 0 або 1.",
                 line=mmo.document.line_no, section="DOCUMENT", field_index=15,
                 field_name=DOCUMENT_FIELDS[14].name, value=fields[14])
        if len(fields) >= 16:
            if not fields[15].strip():
                _add(diags, Severity.WARNING, "MMO_SYNC_METHOD_MISSING",
                     "Код методу синхронізації не вказаний.", line=mmo.document.line_no,
                     section="DOCUMENT", field_index=16, field_name=DOCUMENT_FIELDS[15].name)
            elif fields[15].strip() not in {"1", "2", "3"}:
                _add(diags, Severity.ERROR, "MMO_SYNC_METHOD_INVALID", "Допустимі значення: 1, 2 або 3.",
                     line=mmo.document.line_no, section="DOCUMENT", field_index=16,
                     field_name=DOCUMENT_FIELDS[15].name, value=fields[15])
        if len(fields) >= 17:
            if not fields[16].strip():
                _add(diags, Severity.WARNING, "MMO_AMOUNT_PRECISION_MISSING",
                     "Не задана кількість знаків дробової частини суми.", line=mmo.document.line_no,
                     section="DOCUMENT", field_index=17, field_name=DOCUMENT_FIELDS[16].name)
            elif fields[16].strip() not in {"2", "3", "4"}:
                _add(diags, Severity.ERROR, "MMO_AMOUNT_PRECISION_INVALID", "Допустимі значення: 2, 3 або 4.",
                     line=mmo.document.line_no, section="DOCUMENT", field_index=17,
                     field_name=DOCUMENT_FIELDS[16].name, value=fields[16])

    if mmo.comment:
        _validate_fields(diags, mmo.comment, COMMENT_FIELDS, "COMMENT")

    sync_method = None
    precision = 4
    if mmo.document:
        if len(mmo.document.fields) >= 16:
            sync_method = mmo.document.fields[15].strip() or None
        if len(mmo.document.fields) >= 17 and mmo.document.fields[16].strip() in {"2", "3", "4"}:
            precision = int(mmo.document.fields[16].strip())

    item_totals: list[Decimal] = []
    morion_ids: dict[str, int] = {}
    for item_index, item in enumerate(mmo.items, start=1):
        _validate_field_count(diags, item, len(ITEM_FIELDS), "ITEM", "MMO_ITEM_FIELD_COUNT", item_index=item_index)
        _validate_fields(diags, item, ITEM_FIELDS, "ITEM", item_index=item_index)
        f = item.fields

        if len(f) >= 2 and not f[1].strip():
            _add(diags, Severity.ERROR, "MMO_ITEM_NAME_MISSING", "Найменування товару не вказано.",
                 line=item.line_no, section="ITEM", item_index=item_index, field_index=2,
                 field_name=ITEM_FIELDS[1].name)

        if sync_method == "1" and len(f) >= 1 and not f[0].strip():
            _add(diags, Severity.WARNING, "MMO_PRODUCT_ID_MISSING", "Для методу синхронізації 1 не вказаний ID товару.",
                 line=item.line_no, section="ITEM", item_index=item_index, field_index=1, field_name=ITEM_FIELDS[0].name)
        elif sync_method == "2":
            if len(f) >= 1 and not f[0].strip():
                _add(diags, Severity.WARNING, "MMO_PRODUCT_ID_MISSING", "Для методу 2 не вказаний ID товару.",
                     line=item.line_no, section="ITEM", item_index=item_index, field_index=1, field_name=ITEM_FIELDS[0].name)
            if len(f) >= 3 and not f[2].strip():
                _add(diags, Severity.WARNING, "MMO_MANUFACTURER_ID_MISSING", "Для методу 2 не вказаний ID виробника.",
                     line=item.line_no, section="ITEM", item_index=item_index, field_index=3, field_name=ITEM_FIELDS[2].name)
        elif sync_method == "3" and len(f) >= 5:
            external_id = f[4].strip()
            if not external_id:
                _add(diags, Severity.WARNING, "MMO_MORION_ID_MISSING", "Для методу Morion не вказаний зовнішній ID.",
                     line=item.line_no, section="ITEM", item_index=item_index, field_index=5, field_name=ITEM_FIELDS[4].name)
            elif external_id in morion_ids:
                _add(diags, Severity.ERROR, "MMO_MORION_ID_DUPLICATE",
                     f"Зовнішній ID дублюється з позицією {morion_ids[external_id]}.",
                     line=item.line_no, section="ITEM", item_index=item_index, field_index=5,
                     field_name=ITEM_FIELDS[4].name, value=external_id)
            else:
                morion_ids[external_id] = item_index

        # Arithmetic is checked only when all three values are present and parseable.
        if len(f) >= 21:
            qty = parse_decimal(f[15])
            price = parse_decimal(f[19])
            total = parse_decimal(f[20])
            if total is not None:
                item_totals.append(total)
            if qty is not None and price is not None and total is not None:
                quantum = Decimal("1").scaleb(-precision)
                expected = (qty * price).quantize(quantum, rounding=ROUND_HALF_UP)
                actual = total.quantize(quantum, rounding=ROUND_HALF_UP)
                if expected != actual:
                    _add(diags, Severity.ERROR, "MMO_ITEM_TOTAL_MISMATCH",
                         f"Кількість × ціна = {expected}, але сума = {actual}.",
                         line=item.line_no, section="ITEM", item_index=item_index, field_index=21,
                         field_name=ITEM_FIELDS[20].name, value=f[20])

    if mmo.document and len(mmo.document.fields) >= 13 and item_totals:
        doc_total = parse_decimal(mmo.document.fields[12])
        if doc_total is not None:
            calc_total = sum(item_totals, Decimal("0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            actual_total = doc_total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            if calc_total != actual_total:
                _add(diags, Severity.ERROR, "MMO_DOCUMENT_TOTAL_MISMATCH",
                     f"Сума позицій = {calc_total}, але 'Сума з ПДВ' = {actual_total}.",
                     line=mmo.document.line_no, section="DOCUMENT", field_index=13,
                     field_name=DOCUMENT_FIELDS[12].name, value=mmo.document.fields[12])

    # Stable ordering: errors first, then warnings, then info; inside severity by line/item/field.
    diags.sort(key=lambda d: (-int(d.severity), d.line or 0, d.item_index or 0, d.field_index or 0, d.code))
    return ValidationResult(mmo=mmo, diagnostics=diags)


def open_and_validate(path: str | Path) -> ValidationResult:
    return validate_mmo(parse_mmo(path))
