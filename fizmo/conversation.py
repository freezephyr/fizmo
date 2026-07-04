from __future__ import annotations

from dataclasses import dataclass, field
from time import time

from fizmo.ai.interfaces import SpeechToText, TextModel, TextResponse, Transcription
from fizmo.hardware.interfaces import AudioSample, Display, Microphone
from fizmo.models import RobotState
from fizmo.state.estimator import StateEstimator


@dataclass(frozen=True)
class ConversationTurn:
    audio: AudioSample
    transcription: Transcription
    response: TextResponse
    state: RobotState
    timestamp: float = field(default_factory=time)


@dataclass
class ConversationService:
    microphone: Microphone
    speech_to_text: SpeechToText
    text_model: TextModel
    display: Display
    state: StateEstimator

    def run_once(self, duration_s: float | None = None) -> ConversationTurn:
        self.display.show_face("listening")
        audio = self.microphone.listen(duration_s)

        self.display.show_face("thinking")
        transcription = self.speech_to_text.transcribe(audio)
        robot_state = self.state.read()
        response = self.text_model.respond(transcription.text, robot_state)

        self.display.show_face("responding", response.text[:32])
        return ConversationTurn(
            audio=audio,
            transcription=transcription,
            response=response,
            state=robot_state,
        )
