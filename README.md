# MMO Viewer

Read-only desktop previewer and validator for ANR `*.MMO` electronic invoices.

## Stack

- Python 3.13
- micromamba (portable development environment)
- PySide6 / Qt Widgets
- QSS theme
- pytest
- GitHub Actions

## Current scope (v0.1 foundation)

- open `.mmo` via dialog or Drag & Drop;
- detect/preview CP1251 and UTF-8 files;
- preserve empty and trailing TAB fields;
- parse 4 MMO sections;
- validate 4 / 17 / 1 / 21 field contract;
- validate signature/version, max widths, dates and numbers;
- basic business diagnostics (sync method, totals);
- tabs: Invoice / Items / Diagnostics / RAW;
- read-only: source MMO is never modified.

## Portable setup on Windows

1. Put `micromamba.exe` into `tools\micromamba.exe`.
2. Run `setup-env.cmd`.
3. Run `run.cmd`.
4. Run tests with `test.cmd`.

The environment is kept under `.mamba\` and is intentionally ignored by Git.
Do **not** copy `.mamba\` between PCs; recreate it with `setup-env.cmd`.

## GitHub

Suggested first push:

```bat
git init
git add .
git commit -m "MMO-1: bootstrap PySide6 MMO Viewer"
git branch -M main
git remote add origin <YOUR_GITHUB_REPOSITORY_URL>
git push -u origin main
```

Then create `develop` and use feature branches such as `feature/MMO-3-parser`.

## Contract source

See `docs/MMO_FORMAT_V1.md` and `docs/SOURCE_NOTES.md`.
