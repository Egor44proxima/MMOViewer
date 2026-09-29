# MMO Viewer

Read-only desktop previewer and validator for ANR `*.MMO` electronic invoices.

## Stack

- Python 3.13
- micromamba
- PySide6 / Qt Widgets
- QSS theme
- pytest
- GitHub Actions

## Current scope (MMO-3.1 full Items projection)

- open `.mmo` via dialog or Drag & Drop;
- detect/preview CP1251 and UTF-8 files;
- preserve empty and trailing TAB fields as RAW evidence;
- parse 4 MMO sections;
- support the documented legacy `4 / 17 / 1 / 21` contract through an explicit `Legacy v3 · 17/21` profile;
- support the observed production v3 item extension through an explicit `Production v3 · 17/22 · UKTZED` profile;
- accept one terminal empty TAB field for observed production Header/Item records without discarding it from RAW;
- treat whitespace-only numeric values as empty;
- validate signature/version, dates and numbers;
- report documented legacy width overruns as warnings rather than hard structural errors;
- validate line totals and VAT-aware document totals;
- tabs: `Накладна` / `Товари` / `Діагностика` / `RAW`;
- show the operational columns first in the Items table, then expose every remaining confirmed ITEM field with horizontal scrolling;\n- for unsupported layouts, show all physical ITEM fields only as generic `Fxx · RAW` columns without assigning business semantics;
- explicitly reject the observed problematic `DOCUMENT=18 / ITEM=24` layout as an unconfirmed format variant;
- run profile-specific field, Morion/UKTZED and totals semantics only for a structurally supported document-wide layout;
- reject mixed legacy/production ITEM layouts within one document;
- detect `SUPPORTED` / `AMBIGUOUS` / `UNSUPPORTED` profile state independently from raw parsing;
- keep the parser structure-only: it preserves physical evidence first, while profile detection is a separate read-model step;
- expose the detected profile in diagnostics and RAW view;
- read-only: the source MMO is never modified.

## Windows development environment

The project source tree is portable, but the micromamba environment is intentionally kept outside the repository at:

```text
C:\mmo-mamba
```

This short root path avoids Windows path-length problems caused by deep Qt/PySide6 package trees.

The command scripts use the same environment root:

- `setup-env.cmd` — creates/recreates the `mmoviewer` environment;
- `check-env.cmd` — verifies Python and PySide6;
- `run.cmd` — starts MMO Viewer through `launcher.py`;
- `test.cmd` — runs the test suite.

### First setup

1. Put `micromamba.exe` into `tools\micromamba.exe`.
2. Run `setup-env.cmd`.
3. Run `check-env.cmd`.
4. Run `run.cmd`.
5. Run tests with `test.cmd`.

`tools\micromamba.exe` is a local development tool and is intentionally ignored by Git.

Do not copy `C:\mmo-mamba` between computers. Clone/copy the source repository and recreate the environment with `setup-env.cmd` on each Windows machine.

A legacy/local `.mamba\` directory is also ignored if one is created during experiments, but it is not the canonical environment location.

## Repository

```text
https://github.com/Egor44proxima/MMOViewer.git
```

The default branch is `main`. Feature/fix work should be done on dedicated branches and merged after verification.

## Contract source

See `docs/MMO_FORMAT_V1.md` and `docs/SOURCE_NOTES.md`.

The legacy contract is based on the supplied ANR HTA description. Production extensions are accepted only when supported by observed MMO evidence and regression tests. Unsupported layouts must still be investigated before being classified as format errors.
