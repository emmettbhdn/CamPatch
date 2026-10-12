# CamPatch

CamPatch is a Python CLI foundation for matching physical lighting fixtures to
a DMX patch plan using RDM and an IP Webcam camera. It is deliberately safe:
without `--node` it parses and displays the patch plan only, and it never
writes addresses unless `--apply` is supplied and confirmed.

## Installation

```powershell
py -m venv .venv
.venv\Scripts\pip install -e .
```

The editable installation provides both commands:

```powershell
campatch --help
python -m campatch.cli --help
```

The first command is the installed console script. The second is useful when
working directly from a checkout or when the virtual environment's scripts
directory is not on `PATH`.

## PDF-only usage

The current supported input is a **single-page PDF** containing the fixture
patch information. The parser extracts each fixture's:

* DMX start address, such as `301A`
* Art-Net universe, such as `3`
* patch channel, such as `403#`
* operating mode
* fixture type
* symbol coordinates from the PDF

The former multi-page example was reduced to this patch page. Rigging, power,
and distance pages are not part of the input format.

Parse and display the fixture table without using a camera, Art-Net, or RDM:

```powershell
campatch Example\Example-Patch.pdf
```

The explicit equivalent is:

```powershell
campatch Example\Example-Patch.pdf --list-plan
```

Both commands are safe PDF-only dry runs. They should report 39 fixtures for
the included example. A PDF with zero or multiple pages exits with an error.

## Command-line options

```text
usage: campatch [-h] [--node IP] [--apply] [--list-plan] pdf
```

| Option | Purpose |
| --- | --- |
| `pdf` | Required path to a single-page patch-plan PDF. |
| `-h`, `--help` | Show command usage, examples, and safety notes. |
| `--list-plan` | Print the parsed fixture table and stop before discovery. |
| `--node IP` | Select the Art-Net node for the discovery workflow. |
| `--apply` | After proposed assignments are displayed, ask for confirmation before writes. |

### Review-only hardware workflow

When `--node` is provided without `--apply`, CamPatch is intended to discover
fixtures and print proposed assignments for review:

```powershell
campatch Example\Example-Patch.pdf --node 192.168.1.50
```

Adding `--apply` enables the final confirmation prompt:

```powershell
campatch Example\Example-Patch.pdf --node 192.168.1.50 --apply
```

Do not use `--apply` on live equipment until the node-specific RDM adapter has
been implemented and tested. The current Art-Net transport deliberately raises
`NotImplementedError` instead of sending incomplete discovery, IDENTIFY, or
address-write packets.

## Current implementation status

Implemented:

* One-page PDF validation and patch-plan extraction.
* Typed models for DMX addresses, planned fixtures, discovered fixtures, camera
  points, and proposed assignments.
* Safe dry-run transport and workflow boundaries.
* IP Webcam still-image download helper.
* Four-point camera calibration input parsing.
* Pure matching helpers and test coverage for the PDF and camera parsers.

Not yet implemented:

* An interactive camera window for clicking the four truss corners.
* Image decoding, fixture detection, and perspective transformation.
* RDM discovery and response handling over Art-Net.
* Per-fixture IDENTIFY sequencing and visual confirmation.
* Verified `DMX_START_ADDRESS` writes and response/error handling.

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

## Development and testing

```powershell
.venv\Scripts\python -m pytest
```

The project is split into small modules. See `docs/ARCHITECTURE.md` for
extension points and live-use safety notes.

## Project information needed for the next phase

The following details would be useful or necessary to continue toward live
operation:

1. **Art-Net node**: manufacturer, model, firmware version, IP address scheme,
   and whether it supports Art-Net 3/4 RDM (`ArtRdm`) or another RDM mode.
2. **RDM behavior**: a node manual or packet/API documentation, especially
   discovery, `IDENTIFY_DEVICE`, `DMX_START_ADDRESS`, response timing, and
   whether the node requires a manufacturer-specific mode.
3. **Fixture inventory**: fixture UIDs, manufacturers, models, current
   addresses, personalities/modes, and the intended universe/address rules.
4. **Camera setup**: IP Webcam URL format, phone orientation, resolution,
   camera viewpoint, and whether fixtures are expected to be detected by
   illuminated output, body shape, or both.
5. **Calibration workflow**: which four points the user will click and whether
   the patch-plan coordinates represent a front elevation, top view, or another
   projection.
6. **Matching policy**: what to do when a fixture is missing, duplicated,
   occluded, or ambiguous; manual correction is likely safer than guessing.
7. **Confirmation policy**: whether all assignments should be confirmed at
   once or one fixture at a time, and whether writes should be verified by
   reading the address back.

Providing a node model and a capture of its RDM/Art-Net documentation is the
most important next step before implementing live network traffic.
