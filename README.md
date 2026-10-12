# CamPatch

CamPatch is a Python CLI foundation for matching physical lighting fixtures to
a DMX patch plan using RDM and an IP Webcam camera. It is deliberately safe:
without `--node` it parses and displays the patch plan only, and it never
writes addresses unless `--apply` is supplied and confirmed.

## Quick start

```powershell
py -m venv .venv
.venv\Scripts\pip install -e .
campatch Example\Example-Patch.pdf --list-plan
```

The patch plan must contain exactly one page containing the fixture/DMX data.
The parser extracts
the address (`301A`), universe (`3`), patch channel (`403#`), mode, fixture
name, and the PDF coordinates of each symbol. The former multi-page example
was reduced to this patch page; pages describing rigging, power, and distances
are not part of the input format.

## Hardware status

`campatch.rdm` defines the transport boundary and a dry-run implementation.
`ArtNetRdmTransport` validates the node endpoint but intentionally raises
instead of sending incomplete RDM packets: Art-Net RDM packet framing and
discovery behavior vary by node firmware. A node-specific adapter should
implement discovery, IDENTIFY, and `DMX_START_ADDRESS` writes before using
`--apply` on live equipment.

The IP Webcam still-image endpoint is available through
`campatch.camera.fetch_snapshot`. Camera calibration is represented as four
user-selected points (`x,y;x,y;x,y;x,y`); a GUI/detector can be added without
changing the patch parser or RDM workflow.

## Development

```powershell
.venv\Scripts\python -m pytest
```

See `docs/ARCHITECTURE.md` for extension points and live-use safety notes.
