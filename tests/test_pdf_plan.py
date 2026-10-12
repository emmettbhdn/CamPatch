from pathlib import Path

import pytest
from pypdf import PdfReader, PdfWriter

from campatch.pdf_plan import read_patch_plan


def test_one_page_example_contains_all_fixture_records() -> None:
    fixtures = read_patch_plan(Path("Example") / "Example-Patch.pdf")
    assert len(fixtures) == 39
    assert fixtures[0].address.address == 301
    assert fixtures[0].address.universe == 3
    assert fixtures[0].fixture_type == "Martin Mac Quantum Wash"


def test_parser_retains_plan_coordinates() -> None:
    fixtures = read_patch_plan(Path("Example") / "Example-Patch.pdf")
    assert fixtures[0].pdf_x > 0
    assert fixtures[0].pdf_y > 0


def test_parser_rejects_multi_page_patch_plan(tmp_path: Path) -> None:
    source = PdfReader(Path("Example") / "Example-Patch.pdf")
    writer = PdfWriter()
    writer.add_page(source.pages[0])
    writer.add_blank_page()
    multi_page = tmp_path / "multi-page.pdf"
    with multi_page.open("wb") as output:
        writer.write(output)

    with pytest.raises(ValueError, match="exactly one page"):
        read_patch_plan(multi_page)
