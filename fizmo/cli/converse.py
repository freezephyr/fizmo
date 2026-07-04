from __future__ import annotations

import argparse

from fizmo.hardware.mock import MockMicrophone
from fizmo.runtime import build_mock_runtime


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one Fizmo conversation turn.")
    parser.add_argument("--duration", type=float, default=None, help="Seconds to listen.")
    parser.add_argument("--mock-rms", type=float, default=0.0, help="Mock microphone signal level.")
    args = parser.parse_args()

    runtime = build_mock_runtime()
    if isinstance(runtime.conversation.microphone, MockMicrophone):
        runtime.conversation.microphone.rms = args.mock_rms
    turn = runtime.conversation.run_once(duration_s=args.duration)
    print(
        {
            "transcription": turn.transcription.text,
            "transcription_provider": turn.transcription.provider,
            "response": turn.response.text,
            "response_provider": turn.response.provider,
            "audio_rms": turn.audio.rms,
            "display_expression": runtime.interaction.display.expression,
            "display_text": runtime.interaction.display.text,
        }
    )


if __name__ == "__main__":
    main()
