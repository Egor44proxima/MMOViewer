from pathlib import Path

from mmo_viewer.core.models import Severity
from mmo_viewer.core.validator import open_and_validate

FIXTURES = Path(__file__).parent / "fixtures"


def codes(result):
    return {d.code for d in result.diagnostics}


def test_valid_minimal_has_no_errors():
    result = open_and_validate(FIXTURES / "valid_minimal.mmo")
    assert result.status == "VALID"
    assert not result.errors


def test_trailing_tabs_are_structural_errors():
    result = open_and_validate(FIXTURES / "invalid_trailing_tabs.mmo")
    assert result.status == "INVALID"
    assert "MMO_HEADER_FIELD_COUNT" in codes(result)
    assert "MMO_ITEM_FIELD_COUNT" in codes(result)


def test_invalid_total_is_detected():
    result = open_and_validate(FIXTURES / "invalid_total.mmo")
    assert "MMO_ITEM_TOTAL_MISMATCH" in codes(result)
