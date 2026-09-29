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

Completely empty physical detail lines after the Comment section are skipped by the parser, matching the current legacy-compatible parser behavior. Non-empty lines, including lines containing TAB-separated empty fields, are preserved.

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

For the currently confirmed production path, each VAT-inclusive line projection is rounded to 2 decimal places with `ROUND_HALF_UP`, then those rounded line projections are summed and the final comparison amount is kept at 2 decimal places. This is the behavior implemented by the validator; no alternative rounding model is inferred for unsupported layouts.

## Dates

The HTA declares width 10 but its embedded example uses `DD.MM.YY`; supplied modern samples use `DD.MM.YYYY`.
The validator accepts both forms.

## Decimal separator

The HTA example uses a dot while observed production files use a comma. Both separators are accepted for numeric parsing.


## Problematic 18/24 sample classification (MMO-2.2a)

The file `2026-09-28_11-U163954808-4.mmo` is retained as **problem evidence**, not as proof of a valid production profile.

Observed physical facts may still be recorded for diagnostics:

- Document has 18 fields.
- Item rows have 24 physical fields.
- the file contains values that resemble GTIN, Morion and UKTZED identifiers.
- arithmetic relationships inside the file can be inspected.

However, those observations **do not establish a canonical MMO contract**. Therefore MMO Viewer must not infer that:

- Document field 18 is an officially supported contract field;
- Item field 5 is canonically GTIN for a new profile;
- Item field 22 is canonically Morion for a new profile;
- Item field 23 is canonically UKTZED for a new profile;
- the 18/24 layout is valid merely because its internal arithmetic is coherent.

Until the same layout is confirmed by a known-good file or authoritative specification, it remains unsupported and is reported as a structural error with diagnostic code `MMO_UNCONFIRMED_18_24_LAYOUT`.

The confirmed supported layouts remain those established before MMO-2.2:

- documented legacy Document 17 / Item 21;
- observed production Document 17 / Item 22, with optional terminal TAB where already confirmed.


## Semantic isolation for unsupported layouts (MMO-2.2b)

Structural recognition and semantic interpretation are separate operations.

Profile-specific semantics are applied only when all of the following are true:

- Document contains exactly the confirmed 17 fields;
- every Item row matches a supported structural shape;
- the Item rows do not mix a confirmed legacy 21-field layout with a confirmed production 22-field layout.

If those conditions are not met, the validator still reports structural diagnostics and keeps RAW evidence, but it does **not**:

- interpret field 5 as the Morion binding key;
- interpret field 22 as UKTZED;
- run profile-specific field type/width diagnostics for unsupported Item rows;
- run quantity/price/amount, VAT or document-total business checks for the unsupported layout.

The UI follows the same isolation rule: profile-specific Morion ID and UKTZED columns show no inferred value for unsupported layouts; the original values remain available in RAW.

A document that mixes confirmed legacy and production Item layouts is INVALID with diagnostic code `MMO_ITEM_LAYOUT_MIXED`.


## Format profiles and parser separation (MMO-3)

MMO-3 makes the distinction between **physical parsing** and **format interpretation** explicit.

The parser remains evidence-first and format-agnostic:

- decode bytes;
- detect EOL;
- preserve raw text;
- split Header / Document / Comment / Item physical lines;
- preserve empty and terminal TAB fields;
- skip only completely empty detail lines.

The parser does **not** decide that an unknown field is GTIN, Morion, UKTZED, contract number, or any other business concept.

Profile detection runs after parsing and currently exposes three states:

- `SUPPORTED` — a confirmed profile was identified;
- `AMBIGUOUS` — the structure is allowed but the physical evidence is insufficient to choose a single semantic profile safely;
- `UNSUPPORTED` — the structure does not match the confirmed contracts and profile-specific semantics are blocked.

### Registered profiles

`legacy_v3_17_21`

- Label: `Legacy v3 · 17/21`
- Document: 17 fields
- Item: 21 semantic fields
- Morion binding: field 5 for synchronization method 3
- UKTZED: not defined by this profile

`production_v3_17_22_uktzed`

- Label: `Production v3 · 17/22 · UKTZED`
- Document: 17 fields
- Item: 22 semantic fields
- optional one terminal TAB after Item field 22
- Morion binding: field 5 for synchronization method 3
- UKTZED: field 22

### Ambiguous 22-physical-field row

A physical Item row containing exactly 22 fields where the last field is empty is intentionally treated as ambiguous. That shape can represent either:

- legacy 21 fields plus one terminal TAB, or
- production 22 fields with an empty UKTZED field.

MMO Viewer therefore validates the shared 21-field semantics but does not infer a UKTZED value from that row unless stronger document-wide production evidence exists.

### Unsupported layouts

The problematic 18/24 sample remains `UNSUPPORTED`. The detector does not register it as a profile. Structural diagnostics and RAW evidence remain available, while profile-specific semantics stay isolated.


## Full Items projection (MMO-3.1)

The `Товари` tab is a presentation layer over the resolved format profile; it does not define new format semantics.

For `SUPPORTED` profiles:

- the operational columns are shown first: Morion ID, UKTZED (when defined by the profile), product, unit, quantity, price and amount;
- every other semantic ITEM field from the matched profile is also shown once, labeled as `Fxx · <field name>`;
- the table uses horizontal scrolling instead of dropping fields;
- a physical terminal TAB remains RAW evidence and is not promoted to a semantic column.

For `AMBIGUOUS` layouts:

- only semantics shared safely by the confirmed layouts are named;
- unclassified physical fields are shown generically as `Fxx · RAW`.

For `UNSUPPORTED` layouts:

- no Morion/UKTZED or other business meaning is inferred for unknown positions;
- all physical ITEM fields are still visible as generic `Fxx · RAW` columns;
- this preserves inspection capability without weakening semantic isolation.

The RAW tab remains the canonical byte/text evidence view.


## Frozen operational columns & RAW inspector (MMO-3.2)

The `Товари` tab is split into two synchronized panes.

The left pane is frozen and keeps the operational context visible:

- №
- Статус
- Morion ID
- УКТ ЗЕД
- Товар
- Од.
- К-сть
- Ціна
- Сума

The right pane contains all remaining profile/detail fields and is horizontally scrollable.

Both panes:

- represent the same Item rows;
- share row selection;
- synchronize vertical scrolling;
- remain read-only.

For unsupported layouts the frozen business fields remain blank/unknown and the right pane exposes the physical evidence only as generic `Fxx · RAW` fields.

Selecting a field in the right pane updates the RAW Inspector below the tables. The inspector shows:

- selected row number;
- physical field number;
- whether the field is confirmed semantic data or RAW/unconfirmed evidence;
- the complete field value without inventing additional semantics.

This is a UI/read-model feature only; it does not change parsing, profile detection or validation contracts.
