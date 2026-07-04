from __future__ import annotations

import argparse
import wave
from pathlib import Path

from fizmo.config import load_robot_config
from fizmo.hardware.microphone import AlsaMicrophone
from fizmo.hardware.interfaces import AudioSample
from fizmo.hardware.mock import MockDisplay, MockImuSensor, MockMicrophone, MockServoBus, MockSpeaker
from fizmo.state.estimator import StateEstimator
from fizmo.tools.display import InteractionTools


def main() -> None:
    parser = argparse.ArgumentParser(description="Listen through Fizmo's configured microphone.")
    parser.add_argument("--real", action="store_true", help="Use the configured Raspberry Pi microphone.")
    parser.add_argument("--duration", type=float, default=None, help="Seconds to listen.")
    parser.add_argument("--save-wav", type=Path, default=None, help="Optional path to save captured audio.")
    args = parser.parse_args()

    config = load_robot_config()
    microphone = AlsaMicrophone(config.audio) if args.real else MockMicrophone(
        sample_rate_hz=config.audio.sample_rate_hz,
        channels=config.audio.channels,
        sample_width_bytes=config.audio.sample_width_bytes,
    )

    if args.save_wav is not None:
        sample = microphone.listen(duration_s=args.duration)
        _write_wav(args.save_wav, sample.pcm, sample.sample_rate_hz, sample.channels, sample.sample_width_bytes)
        print(_sample_summary(sample, config.audio.speech_rms_threshold))
        print(f"saved_wav={args.save_wav}")
        return

    state = StateEstimator(imu=MockImuSensor(), config=config, servos=MockServoBus())
    tools = InteractionTools(
        display=MockDisplay(),
        speaker=MockSpeaker(),
        microphone=microphone,
        audio_config=config.audio,
        state=state,
    )
    result = tools.listen(duration_s=args.duration)
    print(result)


def _write_wav(path: Path, pcm: bytes, sample_rate_hz: int, channels: int, sample_width_bytes: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(sample_width_bytes)
        wav.setframerate(sample_rate_hz)
        wav.writeframes(pcm)


def _sample_summary(sample: AudioSample, speech_rms_threshold: float) -> dict[str, float | int | bool]:
    return {
        "duration_s": sample.duration_s,
        "sample_rate_hz": sample.sample_rate_hz,
        "channels": sample.channels,
        "sample_width_bytes": sample.sample_width_bytes,
        "byte_count": len(sample.pcm),
        "rms": sample.rms,
        "speech_rms_threshold": speech_rms_threshold,
        "heard_signal": sample.rms >= speech_rms_threshold,
    }


if __name__ == "__main__":
    main()
