"""Command-line entry point for CamPatch."""

from __future__ import annotations

import argparse
import sys

from .pdf_plan import read_patch_plan, summarize
from .rdm import ArtNetRdmTransport
from .workflow import apply_assignments, build_assignments


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser while keeping PDF-only use as the default.

    ``argparse`` provides both ``-h`` and ``--help`` automatically. The
    extended epilog makes that help useful to someone reviewing the project
    from a terminal rather than requiring them to open the README first.
    """
    parser = argparse.ArgumentParser(
        description="Inspect a one-page DMX patch plan and prepare RDM fixture addressing.",
        epilog=(
            "Examples:\n"
            "  campatch Example\\Example-Patch.pdf\n"
            "      Parse and display the plan without network traffic.\n"
            "  campatch Example\\Example-Patch.pdf --list-plan\n"
            "      Explicitly request the parsed fixture table.\n"
            "  campatch Example\\Example-Patch.pdf --node 192.168.1.50\n"
            "      Discover fixtures and show proposed assignments (review only).\n"
            "  campatch Example\\Example-Patch.pdf --node 192.168.1.50 --apply\n"
            "      Ask for confirmation before writing addresses; live RDM support\n"
            "      depends on the configured Art-Net node adapter.\n\n"
            "Safety: omitting --node performs a PDF-only dry run. No address is\n"
            "written unless --apply is supplied and the confirmation prompt is accepted."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("pdf", help="path to a patch plan containing exactly one page")
    parser.add_argument(
        "--node",
        metavar="IP",
        help="Art-Net node IPv4 address; omit for a safe PDF-only dry run",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="after review, ask for confirmation before writing RDM addresses",
    )
    parser.add_argument(
        "--list-plan",
        action="store_true",
        help="print the parsed fixture table and exit without discovery",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the safe review/apply flow and return a process exit code."""
    args = build_parser().parse_args(argv)
    try:
        planned = read_patch_plan(args.pdf)
        if args.list_plan:
            print(summarize(planned))
            print(f"\nParsed {len(planned)} fixtures (dry run; no network traffic).")
            return 0
        if not args.node:
            print(summarize(planned))
            print(f"\nParsed {len(planned)} fixtures (dry run; no network traffic).")
            return 0
        transport = ArtNetRdmTransport(args.node)
        assignments = build_assignments(args.pdf, transport)
        for item in assignments:
            print(f"{item.uid} -> {item.planned.address} {item.planned.fixture_type}")
        if not args.apply:
            print("\nReview only. Re-run with --apply to write addresses.")
            return 0
        if input("Apply these RDM addresses? [y/N] ").strip().lower() != "y":
            print("No changes applied.")
            return 0
        apply_assignments(assignments, transport)
        print("Addressing complete.")
        return 0
    except (OSError, ValueError, NotImplementedError) as exc:
        print(f"campatch: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
