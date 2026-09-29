import ast
from pathlib import Path


def test_items_workspace_source_is_valid_python():
    source = Path("src/mmo_viewer/ui/items_workspace.py").read_text(encoding="utf-8")
    ast.parse(source)
