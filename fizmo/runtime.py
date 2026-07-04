from __future__ import annotations

from dataclasses import dataclass

from fizmo.ai.mock import MockSpeechToText, MockTextModel
from fizmo.behavior.deterministic import BehaviorRegistry, build_default_behavior_registry
from fizmo.config import RobotConfig, load_robot_config
from fizmo.conversation import ConversationService
from fizmo.hardware.mock import MockDisplay, MockImuSensor, MockMicrophone, MockServoBus, MockSpeaker
from fizmo.state.imu_filter import FilteredImuSensor
from fizmo.state.estimator import StateEstimator
from fizmo.tools.body import BodyTools
from fizmo.tools.calibration import CalibrationTools
from fizmo.tools.display import InteractionTools


@dataclass
class FizmoRuntime:
    config: RobotConfig
    behaviors: BehaviorRegistry
    state: StateEstimator
    body: BodyTools
    calibration: CalibrationTools
    interaction: InteractionTools
    conversation: ConversationService


def build_mock_runtime(config: RobotConfig | None = None) -> FizmoRuntime:
    if config is None:
        config = load_robot_config()
    servos = MockServoBus()
    raw_imu = MockImuSensor()
    imu = FilteredImuSensor(raw_imu)
    display = MockDisplay()
    speaker = MockSpeaker()
    microphone = MockMicrophone(
        sample_rate_hz=config.audio.sample_rate_hz,
        channels=config.audio.channels,
        sample_width_bytes=config.audio.sample_width_bytes,
    )
    state = StateEstimator(imu=imu, config=config, servos=servos)
    behaviors = build_default_behavior_registry(config)
    speech_to_text = MockSpeechToText(config.speech_to_text)
    text_model = MockTextModel(config.text_model)
    return FizmoRuntime(
        config=config,
        behaviors=behaviors,
        state=state,
        body=BodyTools(servos=servos, state=state, config=config, behaviors=behaviors),
        calibration=CalibrationTools(servos=servos, state=state, config=config),
        interaction=InteractionTools(
            display=display,
            speaker=speaker,
            microphone=microphone,
            audio_config=config.audio,
            state=state,
        ),
        conversation=ConversationService(
            microphone=microphone,
            speech_to_text=speech_to_text,
            text_model=text_model,
            display=display,
            state=state,
        ),
    )
