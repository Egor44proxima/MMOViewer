from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DecodedText:
    text: str
    encoding: str
    bom: bool


def decode_mmo(data: bytes) -> DecodedText:
    """Decode without silently replacing bytes.

    CP1251 is the expected legacy encoding. UTF-8 is accepted for preview and
    later reported by the validator as non-standard.
    """
    if data.startswith(b"\xef\xbb\xbf"):
        return DecodedText(data.decode("utf-8-sig"), "utf-8", True)

    # ASCII is valid CP1251 too; prefer the documented legacy contract.
    if all(b < 0x80 for b in data):
        return DecodedText(data.decode("cp1251"), "cp1251", False)

    try:
        text_utf8 = data.decode("utf-8")
    except UnicodeDecodeError:
        text_utf8 = None

    if text_utf8 is not None:
        return DecodedText(text_utf8, "utf-8", False)

    return DecodedText(data.decode("cp1251"), "cp1251", False)


def detect_eol(data: bytes) -> str:
    crlf = data.count(b"\r\n")
    # Remove CRLF before counting standalone LF/CR.
    remainder = data.replace(b"\r\n", b"")
    lf = remainder.count(b"\n")
    cr = remainder.count(b"\r")
    if crlf and not lf and not cr:
        return "CRLF"
    if lf and not crlf and not cr:
        return "LF"
    if cr and not crlf and not lf:
        return "CR"
    if not crlf and not lf and not cr:
        return "NONE"
    return "MIXED"
