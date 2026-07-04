from __future__ import annotations

import argparse

from fizmo.config import load_robot_config
from fizmo.logging import clear_logs, prune_logs, summarize_logs


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage fizmo behavior logs.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list")
    subparsers.add_parser("prune")
    clear_parser = subparsers.add_parser("clear")
    clear_parser.add_argument("--confirm", action="store_true")
    args = parser.parse_args()

    config = load_robot_config().logging

    if args.command == "list":
        print(summarize_logs(config))
    elif args.command == "prune":
        result = prune_logs(config)
        print(_format_result(result))
    elif args.command == "clear":
        if not args.confirm:
            parser.error("clear requires --confirm")
        result = clear_logs(config)
        print(_format_result(result))


def _format_result(result: dict[str, list[object]]) -> dict[str, list[str]]:
    return {
        "deleted": [str(path) for path in result["deleted"]],
        "skipped": [str(path) for path in result["skipped"]],
    }


if __name__ == "__main__":
    main()
