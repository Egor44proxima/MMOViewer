# Source notes

The initial implementation was calibrated against two files supplied during development:

- legacy ANR HTA structure description;
- a real draft `237587` MMO example.

Observed source checksums during initial analysis:

- HTA SHA-256: `ca67e34f4d4978809a6417c7adf9ee185bd56d47df1efd8f55e652ffbc4260fb`
- draft MMO SHA-256: `55ef8ae347f90cdb0c0de19a9688e6a7914947bf8f53e90fc37e466779a35fb1`

The real draft is **not** bundled in this repository because it contains source business data. Tests use synthetic fixtures.

Important legacy parser behaviour:

```js
function ParseStrField(prStr)
{
    prStr = prStr + "\\t";
    ...
}
```

This is why the Python parser preserves trailing empty fields rather than applying `rstrip()`.
