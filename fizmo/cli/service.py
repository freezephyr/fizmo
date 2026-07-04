from __future__ import annotations

import argparse
import signal
import time

from fizmo.runtime import build_mock_runtime


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Fizmo service loop.")
    parser.add_argument("--interval", type=float, default=10.0, help="Seconds between idle heartbeats.")
    args = parser.parse_args()

    running = True

    def stop(_signum: int, _frame: object) -> None:
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    runtime = build_mock_runtime()
    runtime.interaction.show_face("idle", "Fizmo ready")

    while running:
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
