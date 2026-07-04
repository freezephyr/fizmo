from __future__ import annotations

from dataclasses import dataclass

from fizmo.behavior.deterministic import BehaviorRegistry, build_default_behavior_registry
from fizmo.config import RobotConfig, load_robot_config
from fizmo.hardware.mock import MockDisplay, MockImuSensor, MockServoBus, MockSpeaker
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


def build_mock_runtime(config: RobotConfig | None = None) -> FizmoRuntime:
    if config is None:
        config = load_robot_config()
    servos = MockServoBus()
    raw_imu = MockImuSensor()
    imu = FilteredImuSensor(raw_imu)
    display = MockDisplay()
    speaker = MockSpeaker()
    state = StateEstimator(imu=imu, config=config, servos=servos)
    behaviors = build_default_behavior_registry(config)
    return FizmoRuntime(
        config=config,
        behaviors=behaviors,
        state=state,
        body=BodyTools(servos=servos, state=state, config=config, behaviors=behaviors),
        calibration=CalibrationTools(servos=servos, state=state, config=config),
        interaction=InteractionTools(display=display, speaker=speaker, state=state),
    )
