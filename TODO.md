# CamPatch implementation roadmap

This document is the hand-off point for future contributors and Copilot
agents. Read it together with `README.md`, `docs/ARCHITECTURE.md`, the current
tests, and recent Git history before changing code.

## Current baseline

The project currently provides:

* A Python package and `campatch` CLI.
* Parsing and validation of the included **single-page** patch-plan PDF.
* Extraction of fixture type, mode, patch channel, universe, DMX address, and
  PDF coordinates.
* Safe PDF-only CLI operation.
* Typed models, matching helpers, camera snapshot/calibration primitives, and
  dry-run RDM transport interfaces.
* Five passing tests.

The project does **not** yet control live fixtures. The current
`ArtNetRdmTransport` deliberately raises `NotImplementedError` for all RDM
operations.

## How to use this TODO

Implement items in dependency order. Keep hardware-affecting behavior behind
the transport interface, add tests before live-network work, and update this
file when an item is completed or its design changes. Do not claim live
addressing works until discovery, identification, writes, read-back
verification, and failure handling are all implemented and tested.

---

## 1. Confirm and formalize the patch-plan input contract

**Feature:** Make the one-page PDF parser reliable for the patch-plan formats
that will actually be used.

**Work required:**

* Collect representative one-page PDFs exported by the intended lighting
  design software.
* Compare their text token order and coordinate behavior with
  `campatch/pdf_plan.py`.
* Support harmless layout variations such as fixture names containing more or
  fewer text lines, while preserving record boundaries.
* Detect malformed or incomplete fixture records and report their locations
  instead of silently skipping them.
* Validate duplicate patch channels, duplicate universe/address combinations,
  invalid DMX addresses, and invalid or missing modes.
* Add parser tests for every supported layout and failure mode.

**Information needed:**

* The software that exports the patch PDFs.
* At least two or three representative one-page patch plans.
* Whether `A`, `#`, and `U` are guaranteed to be present or are only features
  of the example export.
* The intended rules for duplicate addresses and universe numbering.

**Done when:** Supported plans parse deterministically, malformed records
produce actionable errors, and the parser test suite covers the documented
input contract.

## 2. Add a structured patch-plan export

**Feature:** Export parsed records to JSON and CSV for inspection, debugging,
and later matching/reporting.

**Work required:**

* Add a CLI option such as `--export-json PATH` and/or `--export-csv PATH`.
* Include all parsed fields and PDF coordinates.
* Write files atomically and report filesystem errors clearly.
* Add tests for output schema, ordering, and invalid output paths.

**Information needed:**

* Preferred output formats: JSON, CSV, or both.
* Whether exported coordinates should use PDF points, normalized values, or
  both.
* Whether exports are intended as user deliverables or only diagnostic files.

**Done when:** A user can inspect or archive the parsed patch without reading
terminal output.

## 3. Build the IP Webcam camera client

**Feature:** Add reliable camera configuration and snapshot acquisition for an
IP Webcam phone.

**Work required:**

* Add CLI/configuration support for the camera base URL.
* Support the actual IP Webcam URL, port, and optional authentication format.
* Add connectivity checks, timeouts, useful errors, and retry behavior.
* Validate the response content type and decode the image.
* Optionally save the captured image with a timestamp for review and debugging.
* Add tests using mocked HTTP responses, including timeout, empty response,
  invalid image, and authentication failures.

**Information needed:**

* Phone IP address, IP Webcam port, URL format, and whether authentication is
  enabled.
* Required image resolution and JPEG format.
* Whether the phone is stationary and connected over a reliable local network.
* Whether a single still image or a continuously refreshed stream is required.

**Done when:** The CLI can connect to the configured phone, acquire a decoded
image, and explain all common connection failures without hardware side
effects.

## 4. Implement interactive camera calibration

**Feature:** Let the user click four known points in the camera image and
compute a repeatable mapping into patch-plan coordinates.

**Work required:**

* Add an interactive image window or supported GUI workflow.
* Display the camera image and collect exactly four clicks.
* Enforce a documented click order: top-left, top-right, bottom-right,
  bottom-left, unless a different order is selected.
* Validate that points form a non-degenerate quadrilateral.
* Calculate a perspective transform/homography from camera pixels to the
  patch-plan coordinate space.
* Define the target coordinates and coordinate orientation explicitly.
* Save and reload calibration data, including source image dimensions and
  plan identity, so stale calibration is not reused accidentally.
* Add unit tests for transform calculation and invalid point sets.
* Add a manual/headless calibration input for systems without a GUI.

**Information needed:**

* What the four points represent physically.
* Whether they are the four corners of one planar truss.
* The required click order.
* Whether the PDF is a front elevation, top view, or another projection.
* Whether calibration should be reused between sessions.
* Preferred GUI toolkit and supported operating systems.

**Done when:** A user can create a calibration from four clicks, see the
transformed result, save it, and reload it only when compatible with the
current camera and patch plan.

## 5. Implement fixture detection in camera images

**Feature:** Detect the physical fixtures visible in the calibrated camera
image and return `CameraFixture` candidates.

**Work required:**

* Select and document the detection approach:
  illuminated output, fixture body shape, color/brightness, computer vision
  model, or a hybrid.
* Decode and preprocess images consistently.
* Detect fixture centers or other stable reference points.
* Return calibrated coordinates and confidence scores.
* Handle overlapping, partially hidden, dark, powered-off, and out-of-frame
  fixtures.
* Provide a visual debug overlay showing detections and confidence.
* Add tests using representative images and expected detections.

**Information needed:**

* Sample camera images from the real installation.
* Whether fixtures will be powered and visibly illuminated during detection.
* Fixture models, physical appearance, spacing, and orientation.
* Expected camera resolution, lighting conditions, and occlusion patterns.
* Acceptable false-positive and false-negative rates.

**Done when:** Detection produces reviewable candidate points with confidence
and does not silently treat uncertain detections as facts.

## 6. Integrate calibration, detection, and patch-plan coordinates

**Feature:** Convert detected camera fixtures into patch-plan coordinates and
associate them with planned fixture locations.

**Work required:**

* Pass calibrated `CameraFixture` points into the matching workflow.
* Ensure PDF coordinates and transformed camera coordinates use the same origin,
  scale, and orientation.
* Implement nearest-neighbor matching with a configurable maximum distance.
* Add fixture-type/mode constraints where available.
* Calculate an assignment confidence and identify ambiguous matches.
* Reject or quarantine unmatched, duplicated, missing, or low-confidence
  fixtures.
* Provide a manual correction path before any RDM write.
* Add tests for correct, ambiguous, reversed, missing, and extra-fixture cases.

**Information needed:**

* Matching priority: position, model, mode, existing address, or a combination.
* Maximum acceptable positional error.
* Required behavior for missing, duplicated, occluded, or ambiguous fixtures.
* Whether all planned fixtures must be visible before proceeding.

**Done when:** Every proposed association is explainable, confidence-scored,
reviewable, and cannot silently reuse a planned record.

## 7. Confirm the Art-Net node and RDM protocol

**Feature:** Define the exact live transport contract before implementing
packet generation.

**Work required:**

* Identify the Art-Net node's RDM support and configuration requirements.
* Determine whether it supports Art-Net `ArtRdm`, Art-Net 3/4, or a
  manufacturer-specific API.
* Document network addressing, ports, universes, and discovery behavior.
* Obtain packet/API documentation and, if possible, sanitized packet captures.
* Decide how node responses, timeouts, NACKs, and partial discovery are exposed
  through `RdmTransport`.
* Add protocol constants and typed response/error models rather than embedding
  magic bytes in workflow code.

**Information needed:**

* Node manufacturer, model, firmware, IP address, and configuration export.
* Node manual/protocol documentation.
* Number of nodes and physical topology.
* Whether RDM is enabled and whether the node requires a special mode.
* Any existing controller software known to work with the node.

**Done when:** The exact packet format, response timing, addressing scheme, and
node limitations are documented well enough to write a simulator and a safe
transport implementation.

## 8. Implement RDM discovery over Art-Net

**Feature:** Discover all responding RDM fixtures through the configured
Art-Net node.

**Work required:**

* Build and send the node-compatible discovery request.
* Parse and validate responses and RDM UIDs.
* Implement discovery collision handling and branching/range logic if
  required by the node.
* Query manufacturer, model, software version, current DMX address, and
  personality where supported.
* Add configurable timeout, retry, and cancellation behavior.
* Return deterministic ordering for reproducible review output.
* Add a simulated node and packet-level tests before live testing.
* Log discovery counts and failures without exposing unnecessary sensitive
  network information.

**Information needed:**

* Node protocol details from item 7.
* Required RDM PIDs and supported fixture responses.
* Expected fixture count and a safe test rig.
* Whether discovery may interrupt or affect live DMX output.

**Done when:** Discovery reliably returns typed fixture records and distinguishes
“no fixtures,” “partial discovery,” “node failure,” and “malformed response.”

## 9. Implement per-fixture RDM IDENTIFY sequencing

**Feature:** Identify one discovered fixture at a time so the camera can map it
to a physical fixture.

**Work required:**

* Send `IDENTIFY_DEVICE` enable for exactly one UID.
* Wait for the configured identification interval.
* Capture or refresh the camera image while identification is active.
* Send `IDENTIFY_DEVICE` disable in a `finally`-style cleanup path.
* Confirm the fixture actually responded where the protocol permits.
* Stop safely if disable fails or the user cancels.
* Add dry-run and simulated transport tests for ordering and cleanup.

**Information needed:**

* Fixture identification behavior and required timing.
* Whether identify affects intensity, color, strobe, or other output.
* Identification timeout and user confirmation expectations.
* Whether the node or fixtures support identify while normal DMX is active.

**Done when:** At most one fixture is identified at a time, identify state is
always cleared, and each camera observation is associated with a UID.

## 10. Add the interactive assignment review interface

**Feature:** Show the patch plan, camera image, detected fixtures, proposed
assignments, confidence, and RDM metadata in a user-reviewable interface.

**Work required:**

* Display the calibrated camera image and plan coordinates together.
* Highlight the currently identified fixture.
* Show UID, manufacturer, model, mode, current address, and proposed address.
* Allow correction, rejection, retry, skip, and cancel.
* Require an explicit confirmation before any address write.
* Prevent confirmation when unresolved ambiguities or safety errors remain.
* Preserve a review log suitable for troubleshooting.
* Add UI-independent tests for state transitions and cancellation.

**Information needed:**

* Preferred UI toolkit and whether a desktop GUI is acceptable.
* Whether review should be one fixture at a time or a complete batch.
* Required fields and terminology for the operator.
* Whether keyboard-only operation is needed.

**Done when:** An operator can understand and correct every proposed mapping
before the program is allowed to write an address.

## 11. Implement verified DMX start-address writes

**Feature:** Set each confirmed fixture's DMX start address in the correct
universe and verify the result.

**Work required:**

* Send the node-compatible RDM `SET_COMMAND` for `DMX_START_ADDRESS`.
* Handle one-based DMX addresses and the node's universe mapping correctly.
* Write only confirmed assignments, in a deterministic order.
* Read back the address and verify it matches the requested value.
* Implement retries, timeout handling, NACK/error reporting, and cancellation.
* Decide whether a failed write stops the batch or is recorded and skipped.
* Record old and new addresses for every attempted change.
* Add packet-level, simulated-node, and failure-path tests.

**Information needed:**

* Exact RDM PID encoding and node routing rules.
* Whether fixtures require a reboot, mode change, or separate commit action.
* Whether address writes may overlap with active DMX output.
* Retry policy and required operator behavior after a partial failure.

**Done when:** No write is reported as successful without a verified read-back,
and partial failures produce an unambiguous result report.

## 12. Add end-to-end dry-run and simulation workflows

**Feature:** Exercise the complete process without a camera, node, or live
fixtures.

**Work required:**

* Add a CLI dry-run mode with injected simulated discovery results.
* Add simulated camera points and expected assignment fixtures.
* Simulate identify, timeout, ambiguous matching, write, and read-back failure.
* Make the full workflow deterministic in automated tests.
* Ensure dry-run output clearly states that no network or fixture changes occur.

**Information needed:**

* Representative discovered-fixture records and expected assignments.
* Preferred scenario data for successful and failure demonstrations.
* Whether dry-run data should be supplied by JSON files, CLI options, or
  built-in fixtures.

**Done when:** Contributors can test the complete orchestration on every
device without access to the venue or hardware.

## 13. Add logging, result reports, and recovery support

**Feature:** Make live operation auditable and recoverable.

**Work required:**

* Add structured logging with selectable console/file verbosity.
* Record plan hash, camera/calibration metadata, discovered UIDs, assignments,
  commands, responses, failures, and timestamps.
* Export a final assignment report as JSON/CSV and optionally a human-readable
  report.
* Save enough state to resume or safely rerun after interruption.
* Clearly distinguish planned, attempted, verified, failed, skipped, and
  rolled-back operations.
* Avoid writing credentials or unnecessary personal/network data to logs.
* Add tests for report schemas and interrupted workflows.

**Information needed:**

* Required report format and retention expectations.
* Whether reports need to be imported into lighting-control software.
* Desired log location, verbosity, and privacy constraints.
* Whether rollback means restoring old addresses automatically or only
  producing a recovery list.

**Done when:** Every live run produces an auditable result and an operator can
determine exactly what changed after success, failure, or interruption.

## 14. Harden packaging, configuration, and multi-device development

**Feature:** Make setup repeatable on every development and operator device.

**Work required:**

* Add development dependencies such as pytest to a documented optional
  dependency group instead of requiring manual installation.
* Add formatting, linting, and type-checking configuration if adopted.
* Add CI to run tests and quality checks on pushes and pull requests.
* Document Python version and supported operating systems.
* Add configuration-file support for node, camera, timeouts, and matching
  settings without committing local credentials.
* Keep generated environments, IDE files, caches, and reports out of Git.

**Information needed:**

* Supported Python versions and operating systems.
* Preferred formatter/linter/type checker.
* Whether GitHub Actions may be enabled.
* Preferred configuration format and secret-management approach.

**Done when:** A new device can install documented dependencies, run the full
test suite, and configure local hardware without editing source code or
committing machine-specific files.

