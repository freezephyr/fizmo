from __future__ import annotations

import argparse

from fizmo.logging import DataLogger
from fizmo.runtime import build_mock_runtime


def main() -> None:
    parser = argparse.ArgumentParser(description="Run fizmo tools against mock hardware.")
    parser.add_argument(
        "tool",
        choices=["find_state", "halt", "stand", "sit", "lie_down", "walk", "run", "nod", "tilt_head"],
    )
    parser.add_argument("--steps", type=int, default=2)
    parser.add_argument("--direction", default="left")
    parser.add_argument("--log", action="store_true", help="Record command/result to behavior logs.")
    args = parser.parse_args()

    runtime = build_mock_runtime()
    body = runtime.body

    if args.tool == "walk":
        result = body.walk(steps=args.steps)
    elif args.tool == "run":
        result = body.run(steps=args.steps)
    elif args.tool == "tilt_head":
        result = body.tilt_head(direction=args.direction)
    else:
        result = getattr(body, args.tool)()

    if args.log:
        DataLogger(runtime.config.logging).log_tool_result(args.tool, result)

    print(result)


if __name__ == "__main__":
    main()
