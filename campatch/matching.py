"""Deterministic matching helpers used after camera calibration."""

from __future__ import annotations

from .models import Assignment, CameraFixture, DiscoveredFixture, PlannedFixture


def nearest_plan_fixture(
    camera: CameraFixture, candidates: list[PlannedFixture]
) -> PlannedFixture:
    """Return the plan point nearest to a normalized camera point.

    Squared distance is sufficient here and avoids an unnecessary square-root
    operation while preserving the ordering of candidate distances.
    """
    if not candidates:
        raise ValueError("cannot match against an empty patch plan")
    return min(candidates, key=lambda item: (item.pdf_x - camera.x) ** 2 + (item.pdf_y - camera.y) ** 2)


def propose_assignments(
    discovered: list[DiscoveredFixture],
    planned: list[PlannedFixture],
    camera_points: list[CameraFixture] | None = None,
) -> list[Assignment]:
    """Create reviewable assignments in discovery order.

    Automatic image recognition is deliberately not hidden in this function:
    camera points are supplied by a detector or a future vision plugin.
    """
    if len(discovered) > len(planned):
        raise ValueError("RDM discovered more fixtures than the patch plan contains")
    remaining = list(planned)
    assignments: list[Assignment] = []
    for index, fixture in enumerate(discovered):
        # Remove each selected record so two discovered fixtures cannot receive
        # the same planned address during one proposal pass.
        camera = camera_points[index] if camera_points and index < len(camera_points) else None
        planned_fixture = (
            nearest_plan_fixture(camera, remaining) if camera else remaining[0]
        )
        remaining.remove(planned_fixture)
        assignments.append(Assignment(fixture.uid, planned_fixture, camera))
    return assignments
