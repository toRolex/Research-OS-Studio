"""Leaf CLI for integration facade to call; does not modify the shared CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from research_os.workflows.computational.budget import BudgetUsage
from research_os.workflows.computational.execution import AttemptContext

from .adapter import RemoteAdapter, RemoteReceipt
from .config import RemoteConfig


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Explicit SSH/SLURM lifecycle (never implicit submit/retry)"
    )
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--config", type=Path)
    parser.add_argument("--ledger", default=".research-os/remote-attempts")
    commands = parser.add_subparsers(dest="operation", required=True)
    commands.add_parser("probe")
    submit = commands.add_parser("submit")
    submit.add_argument(
        "--request",
        type=Path,
        required=True,
        help="JSON with context and all six remaining budget dimensions",
    )
    for operation in ("status", "cancel", "log", "artifact"):
        command = commands.add_parser(operation)
        command.add_argument("--attempt", type=int, required=True)
        if operation in {"log", "artifact"}:
            command.add_argument("--path", required=True)
            command.add_argument("--destination", required=True)
        if operation == "artifact":
            command.add_argument("--sha256", required=True)
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        if exc.code == 0:
            return 0
        receipt = RemoteReceipt("usage", "blocked", 2, "invalid CLI arguments")
        print(json.dumps(receipt.as_dict(), sort_keys=True))
        return 2
    try:
        config = RemoteConfig.load(args.config) if args.config else None
        adapter = RemoteAdapter(args.project, config, ledger_directory=args.ledger)
        if args.operation == "submit":
            request = json.loads(args.request.read_bytes())
            if set(request) != {"context", "remaining"}:
                raise ValueError("request requires context and remaining")
            context = dict(request["context"])
            context["command"] = tuple(context["command"])
            receipt = adapter.submit(
                AttemptContext(**context),
                BudgetUsage.from_mapping(request["remaining"]),
            )
        elif args.operation == "probe":
            receipt = adapter.probe()
        elif args.operation == "status":
            receipt = adapter.status(args.attempt)
        elif args.operation == "cancel":
            receipt = adapter.cancel(args.attempt)
        elif args.operation == "log":
            receipt = adapter.log(args.attempt, args.path, args.destination)
        else:
            receipt = adapter.retrieve_artifact(
                args.attempt, args.path, args.sha256, args.destination
            )
    except FileNotFoundError as exc:
        receipt = RemoteReceipt(
            args.operation,
            "blocked",
            3,
            "external file/configuration unavailable: " + str(exc),
        )
    except (ValueError, TypeError, KeyError, OSError) as exc:
        receipt = RemoteReceipt(
            args.operation, "blocked", 2, "configuration/usage error: " + str(exc)
        )
    print(json.dumps(receipt.as_dict(), sort_keys=True))
    return receipt.exit_code


if __name__ == "__main__":
    sys.exit(main())
