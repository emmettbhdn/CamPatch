"""Command-line entry point for CamPatch."""

from __future__ import annotations

import argparse
import sys

from .pdf_plan import read_patch_plan, summarize
from .rdm import ArtNetRdmTransport, DryRunTransport
from .workflow import apply_assignments, build_assignments


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Assign RDM fixtures from a PDF patch plan.")
    parser.add_argument("pdf", help="patch-plan PDF; page 5 is used by default")
    parser.add_argument("--page", type=int, default=5, help="one-based fixture page (default: 5)")
    parser.add_argument("--node", help="Art-Net node IP; omit for safe PDF-only dry run")
    parser.add_argument("--apply", action="store_true", help="write addresses after confirmation")
    parser.add_argument("--list-plan", action="store_true", help="print parsed fixtures and exit")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        planned = read_patch_plan(args.pdf, args.page)
        if args.list_plan or not args.node:
            print(summarize(planned))
            if not args.node:
                print(f"\nParsed {len(planned)} fixtures (dry run; no network traffic).")
                return 0
        transport = ArtNetRdmTransport(args.node)
        assignments = build_assignments(args.pdf, transport, args.page)
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
