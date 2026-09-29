# MMO Viewer

Read-only desktop previewer and validator for ANR `*.MMO` electronic invoices.

## Stack

- Python 3.13
- micromamba
- PySide6 / Qt Widgets
- QSS theme
- pytest
- GitHub Actions

## Current scope (v0.1 foundation)

- open `.mmo` via dialog or Drag & Drop;
- detect/preview CP1251 and UTF-8 files;
- preserve empty and trailing TAB fields;
- parse 4 MMO sections;
- validate the documented 4 / 17 / 1 / 21 legacy contract;
- validate signature/version, max widths, dates and numbers;
- basic business diagnostics (sync method, totals);
- tabs: Invoice / Items / Diagnostics / RAW;
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

The current legacy format contract is based on the supplied ANR HTA description. Real-world MMO variants may extend that contract; unsupported/extended layouts must be investigated before being classified as format errors.
