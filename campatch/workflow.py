"""Application workflow coordinating plan parsing, discovery and confirmation."""

from __future__ import annotations

from .models import Assignment
from .matching import propose_assignments
from .pdf_plan import read_patch_plan
from .rdm import RdmTransport


def build_assignments(pdf_path: str, transport: RdmTransport, page: int = 5) -> list[Assignment]:
    planned = read_patch_plan(pdf_path, page)
    return propose_assignments(transport.discover(), planned)


def apply_assignments(assignments: list[Assignment], transport: RdmTransport) -> None:
    """Write reviewed addresses only after the caller has confirmed them."""
    for assignment in assignments:
        transport.set_start_address(assignment.uid, assignment.planned.address.address)
