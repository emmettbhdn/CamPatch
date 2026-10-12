"""RDM transport boundary and Art-Net implementation.

Art-Net RDM support differs between nodes.  The packet builder is isolated so
node-specific discovery/response handling can be added without affecting the
CLI or patch parser.
"""

from __future__ import annotations

import socket
from typing import Protocol

from .models import DiscoveredFixture


class RdmTransport(Protocol):
    """Operations the workflow needs from any RDM/Art-Net implementation."""

    def discover(self) -> list[DiscoveredFixture]: ...
    def identify(self, uid: str, enabled: bool) -> None: ...
    def set_start_address(self, uid: str, address: int) -> None: ...


class ArtNetRdmTransport:
    """UDP transport for an Art-Net node, with explicit safety controls."""

    def __init__(self, host: str, port: int = 6454, timeout: float = 2.0) -> None:
        self.host, self.port, self.timeout = host, port, timeout

    def _send(self, payload: bytes) -> None:
        # This helper centralizes UDP setup for a future node-specific packet
        # implementation; current methods intentionally refuse unsafe writes.
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(self.timeout)
            sock.sendto(payload, (self.host, self.port))

    def discover(self) -> list[DiscoveredFixture]:
        raise NotImplementedError(
            "RDM discovery requires the node's Art-Net RDM implementation; "
            "use --dry-run or provide a node adapter"
        )

    def identify(self, uid: str, enabled: bool) -> None:
        raise NotImplementedError("RDM identify is node-specific; no command was sent")

    def set_start_address(self, uid: str, address: int) -> None:
        raise NotImplementedError("RDM SET_COMMAND requires a node adapter; no command was sent")


class DryRunTransport:
    """Safe transport used by tests and offline workflow experiments."""

    def __init__(self, fixtures: list[DiscoveredFixture] | None = None) -> None:
        self.fixtures = fixtures or []
        self.actions: list[str] = []

    def discover(self) -> list[DiscoveredFixture]:
        self.actions.append("discover")
        return self.fixtures

    def identify(self, uid: str, enabled: bool) -> None:
        self.actions.append(f"identify {uid} {'on' if enabled else 'off'}")

    def set_start_address(self, uid: str, address: int) -> None:
        self.actions.append(f"set {uid} {address}")
