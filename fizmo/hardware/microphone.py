from __future__ import annotations

import math
import shutil
import struct
import subprocess
from dataclasses import dataclass

from fizmo.config import AudioConfig
from fizmo.hardware.interfaces import AudioSample, Microphone


@dataclass
class AlsaMicrophone(Microphone):
    config: AudioConfig

    def listen(self, duration_s: float | None = None) -> AudioSample:
        if shutil.which("arecord") is None:
            raise RuntimeError("arecord was not found. Install ALSA utilities on the Raspberry Pi.")

        requested_duration = self.config.listen_seconds if duration_s is None else duration_s
        capture_seconds = max(1, math.ceil(requested_duration))
        command = [
            "arecord",
            "-q",
            "-D",
            self.config.input_device,
            "-f",
            "S16_LE",
            "-r",
            str(self.config.sample_rate_hz),
            "-c",
            str(self.config.channels),
            "-d",
            str(capture_seconds),
            "-t",
            "raw",
        ]
        completed = subprocess.run(command, check=True, capture_output=True)
        pcm = completed.stdout
        return AudioSample(
            pcm=pcm,
            sample_rate_hz=self.config.sample_rate_hz,
            channels=self.config.channels,
            sample_width_bytes=self.config.sample_width_bytes,
            duration_s=capture_seconds,
            rms=_pcm16_rms(pcm),
        )


def _pcm16_rms(pcm: bytes) -> float:
    if not pcm:
        return 0.0
    sample_count = len(pcm) // 2
    if sample_count == 0:
        return 0.0
    samples = struct.unpack(f"<{sample_count}h", pcm[: sample_count * 2])
    square_sum = sum(sample * sample for sample in samples)
    return math.sqrt(square_sum / sample_count) / 32768.0
