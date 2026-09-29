# Source notes

The implementation is calibrated against source material supplied during development:

- legacy ANR HTA structure description;
- real draft `237587` MMO example;
- real production invoice `mmo-00554701-от--25-08-2026-06-34-17(2).mmo`.

Observed source checksums:

- HTA SHA-256: `ca67e34f4d4978809a6417c7adf9ee185bd56d47df1efd8f55e652ffbc4260fb`
- draft MMO SHA-256: `55ef8ae347f90cdb0c0de19a9688e6a7914947bf8f53e90fc37e466779a35fb1`
- production MMO SHA-256: `9d5ff958f76933fddb55184c3f312d8dd2354a458b5fb9e302467f74875f236b`

Real business MMO files are **not** bundled in this repository. Tests use synthetic fixtures/inline synthetic records that reproduce only the format characteristics required by regression tests.

## Confirmed MMO-2.1 production evidence

The production invoice above provides the following observations:

- CP1251 + CRLF;
- Header has 4 semantic fields plus one terminal TAB;
- Document has 17 fields;
- Item rows contain legacy fields 1..21 plus field 22 = **Код УКТ ЗЕД**, followed by one terminal TAB;
- whitespace-only content occurs in a numeric field and behaves as an empty value;
- Document field 15 is `0`, so Item field 21 line amounts sum to Document field 12 (net);
- applying Item field 9 VAT rates to the line amounts reproduces Document field 13 (gross);
- observed bank/account values exceed old HTA width limits without making the physical format uninterpretable.

Important legacy parser behaviour:

```js
function ParseStrField(prStr)
{
    prStr = prStr + "\\t";
    ...
}
```

This is why the Python parser preserves trailing empty fields rather than applying `rstrip()`.


## MMO-2.2a correction

The previously examined file `2026-09-28_11-U163954808-4.mmo` was supplied as a **problematic file**. It must not be used as positive evidence that a new 18/24 production format is valid.

Its SHA-256 may be retained as investigation evidence:

`57b85fdfa0a6d2842d31663f6321251bd8d3490c08da04c12d52a01a9199fa09`

What remains usable from that sample is limited to observed facts (field counts, raw values, arithmetic relationships). Semantic field assignments and profile acceptance require corroboration from a known-good file or authoritative format documentation.

MMO-2.2a therefore reclassifies the 18/24 structure as unsupported/problematic and adds a dedicated regression ensuring it remains INVALID.


## MMO-2.2b semantic isolation

The 18/24 problematic sample remains investigation evidence only. Structural errors are reported, while profile-specific field semantics and business checks are deliberately suppressed for unsupported layouts.

The same guard applies to mixed supported Item layouts: a single document may not combine confirmed legacy and production Item shapes without an authoritative profile rule. Synthetic regression tests cover both unsupported-layout isolation and mixed-layout rejection.


## MMO-3 profile registry

MMO-3 does not add a new production format. It converts already confirmed evidence into explicit code profiles:

- `legacy_v3_17_21` from the documented legacy contract;
- `production_v3_17_22_uktzed` from the previously corroborated production sample.

The problematic 18/24 file is deliberately absent from the supported registry. Its role remains negative/investigation evidence only.

The parser itself remains independent of the registry so future files can always be opened and inspected in RAW even when no supported profile matches.
