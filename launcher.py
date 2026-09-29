from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

# Keep the source tree importable without installing the package.
sys.path.insert(0, str(SRC))

from mmo_viewer.app import main


if __name__ == "__main__":
    raise SystemExit(main())
