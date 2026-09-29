# MMO format contract v1

This contract is derived from the supplied legacy ANR HTA description and its embedded JScript parser.
It distinguishes **documented legacy rules** from **observed production extensions**.

## Physical representation

- Text file (`*.MMO`), not a binary container.
- Fields are separated by TAB (`0x09`).
- Observed production files use CRLF line endings.
- The supplied ANR HTA declares `Windows-1251`; CP1251 is therefore the expected encoding.
- RAW parsing preserves empty fields and terminal TABs.

## Legacy sections

1. Header — 4 semantic fields.
2. Document requisites — 17 fields.
3. Comment — one line / one field.
4. Detail rows — 21 legacy fields per product row.

The legacy `ParseStrField()` appends a TAB before parsing. Empty and trailing TAB fields therefore remain part of physical evidence and MUST NOT be stripped from RAW input.

## Header

Semantic fields:

1. `РАСХОДНАЯ_НАКЛАДНАЯ` — String(19)
2. Supplier EDRPOU — String(10)
3. Recipient pharmacy EDRPOU — String(10)
4. `версия_3` — String(10)

Observed production files may contain one terminal TAB after field 4. The parser preserves the resulting empty physical field; the validator accepts it as a terminal separator rather than a fifth semantic Header field.

## Document (17)

1. Document number — String(25)
2. Document date — Date(10)
3. Tax invoice number — String(25)
4. Supplier name — String(50)
5. Bank — legacy String(50)
6. Account — legacy String(25)
7. MFO — String(10)
8. Phones — String(30)
9. Supplier address — String(100)
10. License number — String(25)
11. License expiry — Date(10)
12. Amount without VAT — Number(15,2)
13. Amount with VAT — Number(15,2)
14. Payment due date — Date(10)
15. Price includes VAT flag — Number(1,0); documented values 0/1
16. Synchronization method — Number(2,0); documented values 1/2/3
17. Fraction digits for `Сумма отпускная` — Number(1,0); documented values 2/3/4

Synchronization methods from the supplied HTA:

- `1` — Product ID;
- `2` — Product ID + Manufacturer ID;
- `3` — Morion; field 5 (`ID внешний`) is the binding key and must be unique.

Observed production data contains bank/account values longer than the documented legacy limits. MMO-2.1 therefore reports width overruns as **warnings**, not structural errors.

## Comment (1)

1. Comment — String(200)

## Detail row

### Legacy fields 1..21

1. Product ID — String(20)
2. Product name — String(100)
3. Manufacturer ID — String(20)
4. Manufacturer name — String(50)
5. External ID (e.g. Morion) — String(20)
6. Registration number — String(40)
7. Registration date — Date(10)
8. Registration expiry — Date(10)
9. VAT percent — Number(3,0)
10. Max percent from customs price — Number(3,0)
11. Batch/series number — String(16)
12. Certificate number — String(20)
13. Certificate date — Date(10)
14. Expiry date — Date(10)
15. Unit — String(5)
16. Quantity — Number(15,3)
17. Warehouse price — Number(16,4)
18. Customs price — Number(16,4)
19. Supplier markup percent — Number(6,2)
20. Sale price / purchase price for pharmacy — Number(16,4)
21. Sale amount — Number(16,4)

### Observed production extension

22. **Код УКТ ЗЕД** — production v3 extension.

The current evidence establishes the position and semantics of field 22, but does **not** establish a maximum width. MMO-2.1 therefore does not impose an invented width limit for UKTZED.

A production row may also end with one terminal TAB after field 22. The parser preserves this as an empty physical field while the validator treats the row as 22 semantic fields.

## Empty values

Whitespace-only values are observed in numeric production fields. MMO-2.1 treats `" "`, `"   "`, etc. as semantically empty rather than as invalid numbers. RAW text is still preserved unchanged.

## Totals and VAT

Field 21 is the observed line sale amount.

When Document field 15 (`Ціна включає ПДВ`) is `0`:

- sum(Item field 21) is compared with Document field 12 (`Сума без ПДВ`);
- gross line totals are projected from Item field 9 VAT rates and compared with Document field 13 (`Сума з ПДВ`), when VAT data is complete.

When Document field 15 is `1`:

- sum(Item field 21) is compared with Document field 13 (`Сума з ПДВ`).

The validator does not invent a gross projection when VAT data is incomplete.

## Dates

The HTA declares width 10 but its embedded example uses `DD.MM.YY`; supplied modern samples use `DD.MM.YYYY`.
The validator accepts both forms.

## Decimal separator

The HTA example uses a dot while observed production files use a comma. Both separators are accepted for numeric parsing.


## Extended production v3 profile (MMO-2.2)

The supplied production invoice `2026-09-28_11-U163954808-4.mmo` confirms a second v3 layout:

- Header: 4 fields.
- Document: 18 fields.
- Comment: 1 field.
- Item: 24 physical fields = 23 semantic fields + one terminal empty field from the trailing TAB.

### Document field 18

18. **Договір / підстава** — observed value example: `Договiр поставки №1 від 18.01.24`.

The current evidence establishes the semantic role, but not a vendor-independent maximum width.

### Extended Item fields

Fields 1..4 and 6..21 retain the legacy meanings. The extended identifiers are:

5. **GTIN / штрихкод** — observed as 13-digit GTIN values in all 40 positions of the supplied sample.
22. **Код Моріон** — populated and unique for all 40 positions; Document field 16 is synchronization method `3`, so this field is the observed Morion binding key in this extended profile.
23. **Код УКТ ЗЕД** — populated with 4- or 10-digit commodity codes.
24. Empty physical field caused by the terminal TAB; it is preserved in RAW but is not a semantic field.

This profile is selected only when Document has 18 fields. The existing 17-field layouts keep their previous field-5/field-22 semantics.

### Extended arithmetic evidence

For the supplied 40-position invoice:

- sum(Item field 21) = `9853.65`;
- Document field 12 = `9853.65`;
- every Item satisfies Quantity field 16 × Sale price field 20 = Sale amount field 21;
- every Item VAT rate is 7%;
- applying VAT to the full-precision line amounts and rounding the final document gross once gives `10543.41`, exactly matching Document field 13;
- rounding VAT-inclusive totals per line first would produce `10543.39`, so MMO-2.2 uses **document-level final rounding** for this projection.
