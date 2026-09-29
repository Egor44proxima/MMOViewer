# Source notes

The implementation is calibrated against source material supplied during development:

- legacy ANR HTA structure description;
- real draft `237587` MMO example;
- real production invoice `mmo-00554701-от--25-08-2026-06-34-17(2).mmo`;
- extended production invoice `2026-09-28_11-U163954808-4.mmo`.

Observed source checksums:

- HTA SHA-256: `ca67e34f4d4978809a6417c7adf9ee185bd56d47df1efd8f55e652ffbc4260fb`
- draft MMO SHA-256: `55ef8ae347f90cdb0c0de19a9688e6a7914947bf8f53e90fc37e466779a35fb1`
- production MMO SHA-256: `9d5ff958f76933fddb55184c3f312d8dd2354a458b5fb9e302467f74875f236b`
- extended production MMO SHA-256: `57b85fdfa0a6d2842d31663f6321251bd8d3490c08da04c12d52a01a9199fa09`

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


## Confirmed MMO-2.2 extended production evidence

The extended production sample contains 43 physical lines: Header, Document, Comment and 40 Item rows.

Observed layout:

- CP1251 + CRLF;
- Header = 4 fields;
- Document = 18 fields;
- Document field 18 contains the supply agreement / contractual basis;
- every Item row = 24 physical fields;
- Item field 5 contains 13-digit GTIN values;
- Item field 22 contains a unique 5-6 digit Morion code;
- Item field 23 contains UKTZED values;
- Item field 24 is empty and comes from the terminal TAB;
- sync method = 3;
- all 40 line arithmetic checks pass;
- net total = 9853.65;
- gross total = 10543.41;
- VAT = 7% for all 40 items;
- gross projection matches only when full-precision VAT components are summed first and the final document amount is rounded once.

The real business file is not committed to the repository. Only synthetic regression data reproducing these structural and arithmetic properties is used in tests.
