# MMO format contract v1

This contract is derived from the supplied legacy ANR HTA description and its embedded JScript parser.
It intentionally distinguishes **documented format rules** from **quality recommendations**.

## Physical representation

- Text file (`*.MMO`), not a binary container.
- Fields are separated by TAB (`0x09`).
- Legacy examples and supplied file use CRLF line endings.
- The supplied ANR HTA declares `Windows-1251`; CP1251 is therefore treated as the expected encoding.

## Sections

1. Header — 4 fields.
2. Document requisites — 17 fields.
3. Comment — one line / one field.
4. Detail rows — 21 fields per product row.

The legacy `ParseStrField()` appends a TAB and parses every TAB-separated fragment. Therefore empty fields and trailing TABs are meaningful for structural diagnostics and MUST NOT be stripped before validation.

## Header (4)

1. `РАСХОДНАЯ_НАКЛАДНАЯ` — String(19)
2. Supplier EDRPOU — String(10)
3. Recipient pharmacy EDRPOU — String(10)
4. `версия_3` — String(10)

## Document (17)

1. Document number — String(25)
2. Document date — Date(10)
3. Tax invoice number — String(25)
4. Supplier name — String(50)
5. Bank — String(50)
6. Account — String(25)
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

## Comment (1)

1. Comment — String(200)

## Detail row (21)

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

## Dates

The HTA declares width 10 but its embedded example uses `DD.MM.YY`; the supplied modern sample uses `DD.MM.YYYY`.
The v0.1 validator therefore accepts both forms and reports other non-empty forms as errors.

## Decimal separator

The HTA example uses a dot; the supplied sample uses a comma. v0.1 accepts both separators for numeric parsing until importer behaviour is calibrated against confirmed production imports.
