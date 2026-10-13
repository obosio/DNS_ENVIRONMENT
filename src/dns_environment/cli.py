from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dns_environment.inspector import (
    AUTHORITATIVE_SERVERS,
    EXTERNAL_AUTHORITATIVE_SERVERS,
    FORWARD_ZONES,
    REVERSE_ZONES,
    InspectionReport,
    inspect_zones,
)
from dns_environment.reconciliation import load_reconciliation, validate_reconciliation


def cmd_validate(args: argparse.Namespace) -> int:
    path = Path(args.reconciliation).resolve()
    if not path.is_file():
        print(f"Error: Reconciliation file not found: {path}", file=sys.stderr)
        return 1

    try:
        doc = load_reconciliation(path)
        summary = validate_reconciliation(doc)
        print(f"Validation successful for {path.name}:")
        for key, val in summary.items():
            print(f"  {key}: {val}")
        return 0
    except Exception as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1


def cmd_inspect(args: argparse.Namespace) -> int:
    include_reverse = getattr(args, "reverse", False)
    reports = [inspect_zones(zones=list(FORWARD_ZONES))]
    if include_reverse:
        reports.append(
            inspect_zones(
                zones=list(REVERSE_ZONES),
                servers=EXTERNAL_AUTHORITATIVE_SERVERS,
            )
        )

    print("Inspecting Authoritative DNS Servers...")
    for srv in AUTHORITATIVE_SERVERS:
        print(f"  - {srv['id']}: {srv['name']} ({srv['ip']}) - {srv['view']} view, {srv['role']} [{srv['site']}]")

    print("\nRunning SOA synchronization queries...")
    for report in reports:
        for msg in report.summary_messages:
            print(f"  {msg}")

    return 0 if all(report.all_ok for report in reports) else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dns-environment",
        description="DNS Environment management, inspection, and reconciliation CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser(
        "validate", help="Validate external DNS reconciliation inventory"
    )
    validate_parser.add_argument(
        "--reconciliation",
        "-r",
        default="config/external_dns_reconciliation.yaml",
        help="Path to reconciliation YAML file",
    )
    validate_parser.set_defaults(func=cmd_validate)

    inspect_parser = subparsers.add_parser(
        "inspect", help="Inspect live authoritative DNS servers and zone serials"
    )
    inspect_parser.add_argument(
        "--reverse",
        action="store_true",
        help="Include reverse in-addr.arpa zones in inspection",
    )
    inspect_parser.set_defaults(func=cmd_inspect)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
