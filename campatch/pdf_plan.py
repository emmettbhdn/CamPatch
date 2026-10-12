"""Extraction of fixture records from a one-page patch-plan PDF."""

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
    """Return non-empty text tokens together with their PDF coordinates."""
    result: list[tuple[str, float, float]] = []

    def visitor(text, _cm, tm, _font, _size) -> None:
        # pypdf reports a text block at a coordinate; split blocks into lines
        # because each field in the patch-plan record is separately readable.
        for line in text.splitlines():
            value = line.strip()
            if value:
                result.append((value, float(tm[4]), float(tm[5])))

    page.extract_text(visitor_text=visitor)
    return result


def read_patch_plan(path: str | Path) -> list[PlannedFixture]:
    """Read fixture records from the only page in ``path``.

    The plan format places each record in a vertical stack. The address token
    is followed by a literal ``A``, universe, patch channel, ``#``, ``U``,
    mode, and a one- or two-line fixture name. Coordinates are retained for
    camera/plan matching.
    """
    reader = PdfReader(str(path))
    if len(reader.pages) != 1:
        raise ValueError(f"patch plan must contain exactly one page (found {len(reader.pages)})")
    tokens = _tokens(reader.pages[0])
    fixtures: list[PlannedFixture] = []
    for index, (value, x, y) in enumerate(tokens):
        match = _ADDRESS.fullmatch(value)
        # The address and "A" are emitted as separate tokens by the example
        # PDF, so identify a record by this stable two-token prefix.
        if not match or index + 7 >= len(tokens) or tokens[index + 1][0] != "A":
            continue
        universe_match = _UNIVERSE.fullmatch(tokens[index + 2][0])
        patch_match = _PATCH.fullmatch(tokens[index + 3][0])
        mode = tokens[index + 6][0].removeprefix("Mode:").strip()
        name_parts = [tokens[index + 7][0]]
        if index + 8 < len(tokens) and tokens[index + 8][1] == tokens[index + 7][1]:
            # A matching x coordinate indicates the second line of a fixture
            # name rather than the next fixture record.
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
