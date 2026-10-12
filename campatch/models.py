"""Domain models shared by the PDF, camera, matching and RDM layers."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DmxAddress:
    """A one-based DMX address within an Art-Net universe."""

    universe: int
    address: int

    def __post_init__(self) -> None:
        if self.universe < 0:
            raise ValueError("universe must be non-negative")
        if not 1 <= self.address <= 512:
            raise ValueError("DMX address must be between 1 and 512")

    def __str__(self) -> str:
        return f"U{self.universe}:{self.address}"


@dataclass(frozen=True)
class PlannedFixture:
    """A fixture record read from the patch plan."""

    patch_channel: int
    fixture_type: str
    mode: str
    address: DmxAddress
    pdf_x: float
    pdf_y: float


@dataclass(frozen=True)
class DiscoveredFixture:
    """A fixture returned by RDM discovery."""

    uid: str
    manufacturer: str = ""
    model: str = ""
    current_address: int | None = None


@dataclass(frozen=True)
class CameraFixture:
    """A visible fixture represented in camera pixel coordinates."""

    x: float
    y: float
    confidence: float = 1.0


@dataclass(frozen=True)
class Assignment:
    """A proposed relationship between an RDM fixture and a plan address."""

    uid: str
    planned: PlannedFixture
    camera: CameraFixture | None

