"""Camera acquisition and calibration primitives.

IP Webcam exposes a still image endpoint.  The GUI calibration hook is kept
small and optional so headless deployments can provide four points themselves.
"""

from __future__ import annotations

from urllib.request import urlopen


def fetch_snapshot(base_url: str, timeout: float = 5.0) -> bytes:
    """Fetch a JPEG from an IP Webcam server.

    Keeping this function byte-oriented means image decoding can be supplied
    by a later vision implementation without coupling it to network access.
    """
    url = base_url.rstrip("/") + "/photo.jpg"
    with urlopen(url, timeout=timeout) as response:
        data = response.read()
    if not data:
        raise RuntimeError(f"camera returned an empty response from {url}")
    return data


def parse_points(value: str) -> list[tuple[float, float]]:
    """Parse four ``x,y`` points supplied on the command line."""
    points = []
    for item in value.split(";"):
        try:
            x, y = (float(part.strip()) for part in item.split(",", 1))
        except (ValueError, TypeError):
            raise ValueError("points must use x,y;x,y;x,y;x,y") from None
        points.append((x, y))
    # Four corners are required to define a perspective calibration quadrilateral.
    if len(points) != 4:
        raise ValueError("exactly four calibration points are required")
    return points
