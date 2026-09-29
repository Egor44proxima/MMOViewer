from __future__ import annotations

from pathlib import Path


def load_qss() -> str:
    # repository layout: src/mmo_viewer/ui/theme.py -> project root
    root = Path(__file__).resolve().parents[3]
    qss = root / "resources" / "styles" / "main.qss"
    return qss.read_text(encoding="utf-8")
