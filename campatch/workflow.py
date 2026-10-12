"""Application workflow coordinating plan parsing, discovery and confirmation."""

from __future__ import annotations

from .models import Assignment
from .matching import propose_assignments
from .pdf_plan import read_patch_plan
from .rdm import RdmTransport


def build_assignments(pdf_path: str, transport: RdmTransport) -> list[Assignment]:
    """Discover fixtures and pair them with records from the one-page plan."""
    planned = read_patch_plan(pdf_path)
    return propose_assignments(transport.discover(), planned)


def apply_assignments(assignments: list[Assignment], transport: RdmTransport) -> None:
    """Write reviewed addresses only after the caller has confirmed them."""
    for assignment in assignments:
        # The transport is responsible for the protocol-level response and
        # verification; this layer only applies already-reviewed choices.
        transport.set_start_address(assignment.uid, assignment.planned.address.address)
