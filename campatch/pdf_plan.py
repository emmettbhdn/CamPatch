"""Extraction of the fixture table on the final page of a patch-plan PDF."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader

from .models import DmxAddress, PlannedFixture

_ADDRESS = re.compile(r"^(?P<address>\d{1,3})$")
_UNIVERSE = re.compile(r"^(?P<universe>\d{1,3})$")
_PATCH = re.compile(r"^(?P<patch>\d{1,4})$")


def _tokens(page) -> list[tuple[str, float, float]]:
    result: list[tuple[str, float, float]] = []

    def visitor(text, _cm, tm, _font, _size) -> None:
        for line in text.splitlines():
            value = line.strip()
            if value:
                result.append((value, float(tm[4]), float(tm[5])))

    page.extract_text(visitor_text=visitor)
    return result


def read_patch_plan(path: str | Path, page_number: int = 5) -> list[PlannedFixture]:
    """Read fixture records from ``page_number`` (one-based) of a PDF.

    The example plan places each record in a vertical stack.  The address token
    is followed by universe and patch channel tokens, then mode and a two-line
    fixture name.  Coordinates are retained for camera/plan matching.
    """
    reader = PdfReader(str(path))
    if not 1 <= page_number <= len(reader.pages):
        raise ValueError(f"page {page_number} is outside this PDF ({len(reader.pages)} pages)")
    tokens = _tokens(reader.pages[page_number - 1])
    fixtures: list[PlannedFixture] = []
    for index, (value, x, y) in enumerate(tokens):
        match = _ADDRESS.fullmatch(value)
        if not match or index + 7 >= len(tokens) or tokens[index + 1][0] != "A":
            continue
        universe_match = _UNIVERSE.fullmatch(tokens[index + 2][0])
        patch_match = _PATCH.fullmatch(tokens[index + 3][0])
        mode = tokens[index + 6][0].removeprefix("Mode:").strip()
        name_parts = [tokens[index + 7][0]]
        if index + 8 < len(tokens) and tokens[index + 8][1] == tokens[index + 7][1]:
            name_parts.append(tokens[index + 8][0])
        if not universe_match or not patch_match or not mode:
            continue
        fixtures.append(
            PlannedFixture(
                patch_channel=int(patch_match.group("patch")),
                fixture_type=" ".join(name_parts).replace("\n", " ").strip(),
                mode=mode,
                address=DmxAddress(int(universe_match.group("universe")), int(match.group("address"))),
                pdf_x=x,
                pdf_y=y,
            )
        )
    if not fixtures:
        raise ValueError("no fixture records found; check the selected patch-plan page")
    return fixtures


def summarize(fixtures: Iterable[PlannedFixture]) -> str:
    """Return a compact human-readable plan summary."""
    rows = [f"{f.patch_channel:>4}  {f.address!s:<8}  {f.fixture_type} ({f.mode})" for f in fixtures]
    return "\n".join(rows)
