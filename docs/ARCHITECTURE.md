# Architecture

The project is split into small layers:

* `pdf_plan.py` reads only the selected fixture page and returns typed plan
  records with PDF coordinates.
* `camera.py` contains IP Webcam acquisition and calibration input parsing.
* `matching.py` contains pure matching/proposal logic.
* `rdm.py` defines the `RdmTransport` protocol, a safe dry-run transport, and
  the Art-Net node boundary.
* `workflow.py` coordinates discovery, review, and writes.
* `cli.py` is presentation and safety confirmation only.

## Live hardware implementation

Implement a node adapter conforming to `RdmTransport`. It must perform RDM
discovery, send `IDENTIFY_DEVICE` one fixture at a time, wait for responses,
and verify `DMX_START_ADDRESS` after writing. Keep `--apply` confirmation and
per-fixture error reporting in the workflow. Never infer a successful write
from a UDP send alone.

The camera detector should return `CameraFixture` points in the same calibrated
coordinate space as plan points. For ambiguous matches, retain the assignment
as a review item rather than silently choosing a fixture.
