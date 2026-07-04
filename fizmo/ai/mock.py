from __future__ import annotations

from dataclasses import dataclass

from fizmo.ai.interfaces import SpeechToText, TextModel, TextResponse, Transcription
from fizmo.config import SpeechToTextConfig, TextModelConfig
from fizmo.hardware.interfaces import AudioSample
from fizmo.models import RobotState


@dataclass
class MockSpeechToText(SpeechToText):
    config: SpeechToTextConfig
    text: str = "hello fizmo"

    def transcribe(self, audio: AudioSample) -> Transcription:
        if audio.rms <= 0.0:
            return Transcription(text="", confidence=1.0, provider=self.config.provider, model=self.config.model)
        return Transcription(text=self.text, confidence=1.0, provider=self.config.provider, model=self.config.model)


@dataclass
class MockTextModel(TextModel):
    config: TextModelConfig

    def respond(self, user_text: str, robot_state: RobotState) -> TextResponse:
        text = "I did not hear anything." if not user_text.strip() else f"I heard: {user_text}"
        return TextResponse(text=text, provider=self.config.provider, model=self.config.model)
