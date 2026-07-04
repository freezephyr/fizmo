from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from time import time

from fizmo.hardware.interfaces import AudioSample
from fizmo.models import RobotState


@dataclass(frozen=True)
class Transcription:
    text: str
    confidence: float = 0.0
    provider: str = "unknown"
    model: str = "unknown"
    timestamp: float = field(default_factory=time)

    @property
    def has_text(self) -> bool:
        return bool(self.text.strip())


@dataclass(frozen=True)
class TextResponse:
    text: str
    provider: str = "unknown"
    model: str = "unknown"
    timestamp: float = field(default_factory=time)


class SpeechToText(ABC):
    @abstractmethod
    def transcribe(self, audio: AudioSample) -> Transcription:
        raise NotImplementedError


class TextModel(ABC):
    @abstractmethod
    def respond(self, user_text: str, robot_state: RobotState) -> TextResponse:
        raise NotImplementedError
