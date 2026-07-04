from __future__ import annotations

from dataclasses import dataclass

from fizmo.hardware.interfaces import Display, Speaker
from fizmo.models import ToolResult
from fizmo.state.estimator import StateEstimator


@dataclass
class InteractionTools:
    display: Display
    speaker: Speaker
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

