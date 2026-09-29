from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path


class Severity(IntEnum):
    INFO = 10
    WARNING = 20
    ERROR = 30

    @property
    def label(self) -> str:
        return self.name


@dataclass(frozen=True, slots=True)
class Diagnostic:
    severity: Severity
    code: str
    message: str
    line: int | None = None
    section: str = ""
    item_index: int | None = None
    field_index: int | None = None  # 1-based
    field_name: str = ""
    value: str = ""


@dataclass(slots=True)
class ParsedLine:
    line_no: int
    raw: str
    fields: list[str]


@dataclass(slots=True)
class MMOFile:
    path: Path
    encoding: str
    eol: str
    bom: bool
    raw_bytes: bytes
    text: str
    header: ParsedLine | None
    document: ParsedLine | None
    comment: ParsedLine | None
    items: list[ParsedLine] = field(default_factory=list)

    @property
    def item_count(self) -> int:
        return len(self.items)


@dataclass(slots=True)
class ValidationResult:
    mmo: MMOFile
    diagnostics: list[Diagnostic]

    @property
    def errors(self) -> list[Diagnostic]:
        return [d for d in self.diagnostics if d.severity == Severity.ERROR]

    @property
    def warnings(self) -> list[Diagnostic]:
        return [d for d in self.diagnostics if d.severity == Severity.WARNING]

    @property
    def infos(self) -> list[Diagnostic]:
        return [d for d in self.diagnostics if d.severity == Severity.INFO]

    @property
    def status(self) -> str:
        if self.errors:
            return "INVALID"
        if self.warnings:
            return "VALID WITH WARNINGS"
        return "VALID"
