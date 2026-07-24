"""post-incident CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from post_incident.bundle import validate_bundle
from post_incident.diagnostics import Report
from post_incident.lineage import lineage_graph_file, validate_lineage_file
from post_incident.morph import replay_check
from post_incident.preservation import verify_claim_file
from post_incident.redaction import verify_commitment_file
from post_incident.source import validate_source_file


def _print_report(report: Report) -> int:
    sys.stdout.write(report.dumps())
    return int(report.exit_code())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="post-incident",
        description="Offline incident lineage and preservation verification",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    source = sub.add_parser("source", help="Source record commands")
    source_sub = source.add_subparsers(dest="source_cmd", required=True)
    source_validate = source_sub.add_parser("validate")
    source_validate.add_argument("file", type=Path)

    lineage = sub.add_parser("lineage", help="Lineage commands")
    lineage_sub = lineage.add_subparsers(dest="lineage_cmd", required=True)
    lineage_validate = lineage_sub.add_parser("validate")
    lineage_validate.add_argument("file", type=Path)
    lineage_graph = lineage_sub.add_parser("graph")
    lineage_graph.add_argument("file", type=Path)
    lineage_graph.add_argument("--out", type=Path, required=True)

    preservation = sub.add_parser("preservation", help="Preservation claims")
    preservation_sub = preservation.add_subparsers(dest="preservation_cmd", required=True)
    preservation_verify = preservation_sub.add_parser("verify")
    preservation_verify.add_argument("file", type=Path)

    redaction = sub.add_parser("redaction", help="Redaction commitments")
    redaction_sub = redaction.add_subparsers(dest="redaction_cmd", required=True)
    redaction_verify = redaction_sub.add_parser("verify")
    redaction_verify.add_argument("file", type=Path)

    bundle = sub.add_parser("bundle", help="Release bundle commands")
    bundle_sub = bundle.add_subparsers(dest="bundle_cmd", required=True)
    bundle_validate = bundle_sub.add_parser("validate")
    bundle_validate.add_argument("directory", type=Path)

    replay = sub.add_parser("replay-check", help="Morph replay fixture linkage")
    replay.add_argument("directory", type=Path)
    replay.add_argument("--replay-report", type=Path, required=True)

    args = parser.parse_args(argv)

    if args.cmd == "source" and args.source_cmd == "validate":
        return _print_report(validate_source_file(args.file))
    if args.cmd == "lineage" and args.lineage_cmd == "validate":
        return _print_report(validate_lineage_file(args.file))
    if args.cmd == "lineage" and args.lineage_cmd == "graph":
        return _print_report(lineage_graph_file(args.file, args.out))
    if args.cmd == "preservation" and args.preservation_cmd == "verify":
        return _print_report(verify_claim_file(args.file))
    if args.cmd == "redaction" and args.redaction_cmd == "verify":
        return _print_report(verify_commitment_file(args.file))
    if args.cmd == "bundle" and args.bundle_cmd == "validate":
        return _print_report(validate_bundle(args.directory))
    if args.cmd == "replay-check":
        return _print_report(replay_check(args.directory, args.replay_report))

    parser.error("unrecognized command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
