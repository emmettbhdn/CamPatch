from pathlib import Path

from campatch.pdf_plan import read_patch_plan


def test_example_page_contains_all_fixture_records() -> None:
    fixtures = read_patch_plan(Path("Example") / "Example-Patch.pdf")
    assert len(fixtures) == 39
    assert fixtures[0].address.address == 301
    assert fixtures[0].address.universe == 3
    assert fixtures[0].fixture_type == "Martin Mac Quantum Wash"


def test_parser_retains_plan_coordinates() -> None:
    fixtures = read_patch_plan(Path("Example") / "Example-Patch.pdf")
    assert fixtures[0].pdf_x > 0
    assert fixtures[0].pdf_y > 0
