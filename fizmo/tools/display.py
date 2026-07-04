from __future__ import annotations

from dataclasses import dataclass

from fizmo.config import AudioConfig
from fizmo.hardware.interfaces import Display, Microphone, Speaker
from fizmo.models import ToolResult
from fizmo.state.estimator import StateEstimator


@dataclass
class InteractionTools:
    display: Display
    speaker: Speaker
    microphone: Microphone
    audio_config: AudioConfig
    state: StateEstimator

    def show_face(self, expression: str, text: str | None = None) -> ToolResult:
        before = self.state.read()
        self.display.show_face(expression, text)
        after = self.state.read()
        return ToolResult(
            ok=True,
            tool="show_face",
            status="done",
            state_before=before,
            state_after=after,
            data={"expression": expression, "text": text},
        )

    def speak(self, text: str) -> ToolResult:
        before = self.state.read()
        self.display.show_face("speaking", text[:32])
        self.speaker.speak(text)
        self.display.show_face("idle")
        after = self.state.read()
        return ToolResult(ok=True, tool="speak", status="done", state_before=before, state_after=after)

    def listen(self, duration_s: float | None = None) -> ToolResult:
        before = self.state.read()
        self.display.show_face("listening")
        sample = self.microphone.listen(duration_s)
        heard_signal = sample.rms >= self.audio_config.speech_rms_threshold
        self.display.show_face("thinking" if heard_signal else "idle")
        after = self.state.read()
        return ToolResult(
            ok=True,
            tool="listen",
            status="heard_signal" if heard_signal else "silence",
            state_before=before,
            state_after=after,
            data={
                "duration_s": sample.duration_s,
                "sample_rate_hz": sample.sample_rate_hz,
                "channels": sample.channels,
                "sample_width_bytes": sample.sample_width_bytes,
                "byte_count": len(sample.pcm),
                "rms": sample.rms,
                "speech_rms_threshold": self.audio_config.speech_rms_threshold,
                "heard_signal": heard_signal,
            },
        )
