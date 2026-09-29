from __future__ import annotations

from pathlib import Path

from .encoding import decode_mmo, detect_eol
from .models import MMOFile, ParsedLine


def _split_physical_lines(text: str) -> list[str]:
    # splitlines() removes EOL markers but deliberately does NOT strip TABs.
    return text.splitlines()


def _parsed_line(line_no: int, raw: str, *, comment: bool = False) -> ParsedLine:
    fields = [raw] if comment else raw.split("\t")
    return ParsedLine(line_no=line_no, raw=raw, fields=fields)


def parse_mmo_bytes(data: bytes, *, path: Path | str = "<memory>") -> MMOFile:
    decoded = decode_mmo(data)
    lines = _split_physical_lines(decoded.text)

    header = _parsed_line(1, lines[0]) if len(lines) >= 1 else None
    document = _parsed_line(2, lines[1]) if len(lines) >= 2 else None
    comment = _parsed_line(3, lines[2], comment=True) if len(lines) >= 3 else None

    items: list[ParsedLine] = []
    for index, raw in enumerate(lines[3:], start=4):
        # Matches legacy HTA behaviour: completely empty detail lines are skipped.
        if raw == "":
            continue
        items.append(_parsed_line(index, raw))

    return MMOFile(
        path=Path(path),
        encoding=decoded.encoding,
        eol=detect_eol(data),
        bom=decoded.bom,
        raw_bytes=data,
        text=decoded.text,
        header=header,
        document=document,
        comment=comment,
        items=items,
    )


def parse_mmo(path: str | Path) -> MMOFile:
    file_path = Path(path)
    return parse_mmo_bytes(file_path.read_bytes(), path=file_path)
