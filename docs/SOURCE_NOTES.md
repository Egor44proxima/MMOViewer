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
