from __future__ import annotations

from dataclasses import dataclass
from math import cos, radians
from typing import Any

from fizmo.config import RobotConfig
from fizmo.behavior.models import BehaviorModel, BehaviorPlan, ServoFrame
from fizmo.models import RobotState


@dataclass
class PoseBehaviorModel(BehaviorModel):
    name: str
    config: RobotConfig
    target_deg: float

    def plan(self, state: RobotState, **kwargs: Any) -> BehaviorPlan:
        return BehaviorPlan(
            frames=(ServoFrame({servo.name: self.target_deg for servo in self.config.servos}, angle_space="servo"),),
            metadata={"pose_deg": self.target_deg},
        )


@dataclass
class StandLiftBehaviorModel(BehaviorModel):
    name: str
    config: RobotConfig
    leg_angle_deg: float = 10.0
    max_step_deg: float = 8.0
    delay_s: float = 0.08

    def plan(self, state: RobotState, **kwargs: Any) -> BehaviorPlan:
        target_height_mm = self.config.leg_length_mm * cos(radians(self.leg_angle_deg))
        perpendicular_height_mm = self.config.leg_length_mm
        targets = {
            servo.name: self.leg_angle_deg
            for servo in self.config.servos
        }
        frames: list[ServoFrame] = []
        current = {
            servo.name: 0.0
            for servo in self.config.servos
        }

        remaining = True
        while remaining:
            remaining = False
            next_targets: dict[str, float] = {}
            for servo in self.config.servos:
                start = current[servo.name]
                target = targets[servo.name]
                delta = target - start
                if abs(delta) > self.max_step_deg:
                    remaining = True
                    start += self.max_step_deg if delta > 0 else -self.max_step_deg
                else:
                    start = target
                current[servo.name] = start
                next_targets[servo.name] = start
            frames.append(ServoFrame(next_targets, self.delay_s if remaining else 0.0, angle_space="logical"))

        return BehaviorPlan(
            frames=tuple(frames),
            metadata={
                "leg_angle_deg": self.leg_angle_deg,
                "angle_reference": "0_deg_perpendicular_to_ground",
                "leg_length_mm": self.config.leg_length_mm,
                "target_vertical_height_mm": target_height_mm,
                "perpendicular_vertical_height_mm": perpendicular_height_mm,
                "height_delta_from_perpendicular_mm": perpendicular_height_mm - target_height_mm,
                "success_signal": "stable IMU roll/pitch plus geometry-derived target height",
                "imu_height_note": "MPU6050 cannot directly measure static absolute height",
                "imu_roll_deg": state.imu.roll_deg,
                "imu_pitch_deg": state.imu.pitch_deg,
            },
        )


@dataclass
class AlternatingGaitBehaviorModel(BehaviorModel):
    name: str
    config: RobotConfig
    amplitude_deg: float
    delay_s: float
    default_steps: int

    def plan(self, state: RobotState, **kwargs: Any) -> BehaviorPlan:
        steps = max(1, int(kwargs.get("steps", self.default_steps)))
        frames: list[ServoFrame] = []
        for _ in range(steps):
            frames.append(
                ServoFrame(
                    {
                        "front_left": self.amplitude_deg,
                        "rear_right": self.amplitude_deg,
                        "front_right": -self.amplitude_deg,
                        "rear_left": -self.amplitude_deg,
                    },
                    delay_s=self.delay_s,
                    angle_space="logical",
                )
            )
            frames.append(
                ServoFrame(
                    {
                        "front_left": -self.amplitude_deg,
                        "rear_right": -self.amplitude_deg,
                        "front_right": self.amplitude_deg,
                        "rear_left": self.amplitude_deg,
                    },
                    delay_s=self.delay_s,
                    angle_space="logical",
                )
            )
        frames.append(ServoFrame({servo.name: 0.0 for servo in self.config.servos}, angle_space="logical"))
        return BehaviorPlan(
            frames=tuple(frames),
            metadata={"steps": steps, "amplitude_deg": self.amplitude_deg},
        )


@dataclass
class NodBehaviorModel(BehaviorModel):
    name: str
    config: RobotConfig

    def plan(self, state: RobotState, **kwargs: Any) -> BehaviorPlan:
        return BehaviorPlan(
            frames=(
                ServoFrame({"front_left": -12.0, "front_right": -12.0, "rear_left": 8.0, "rear_right": 8.0}, 0.12),
                ServoFrame({"front_left": 10.0, "front_right": 10.0, "rear_left": -6.0, "rear_right": -6.0}, 0.12),
                ServoFrame({servo.name: 0.0 for servo in self.config.servos}),
            )
        )


@dataclass
class TiltHeadBehaviorModel(BehaviorModel):
    name: str
    config: RobotConfig

    def plan(self, state: RobotState, **kwargs: Any) -> BehaviorPlan:
        direction = str(kwargs.get("direction", "left")).lower()
        offsets = {
            "left": {"front_left": -10.0, "rear_left": -10.0, "front_right": 10.0, "rear_right": 10.0},
            "right": {"front_left": 10.0, "rear_left": 10.0, "front_right": -10.0, "rear_right": -10.0},
            "up": {"front_left": 10.0, "front_right": 10.0, "rear_left": -8.0, "rear_right": -8.0},
            "down": {"front_left": -10.0, "front_right": -10.0, "rear_left": 8.0, "rear_right": 8.0},
        }
        if direction not in offsets:
            return BehaviorPlan(frames=(), expected_done=False, confidence=0.0, metadata={"error": direction})

        targets = {servo.name: offsets[direction].get(servo.name, 0.0) for servo in self.config.servos}
        return BehaviorPlan(
            frames=(
                ServoFrame(targets, 0.18),
                ServoFrame({servo.name: 0.0 for servo in self.config.servos}),
            ),
            metadata={"direction": direction},
        )


@dataclass(frozen=True)
class BehaviorRegistry:
    stand: BehaviorModel
    sit: BehaviorModel
    lie_down: BehaviorModel
    walk: BehaviorModel
    run: BehaviorModel
    nod: BehaviorModel
    tilt_head: BehaviorModel


def build_default_behavior_registry(config: RobotConfig) -> BehaviorRegistry:
    return BehaviorRegistry(
        stand=StandLiftBehaviorModel("stand", config, leg_angle_deg=10.0),
        sit=PoseBehaviorModel("sit", config, target_deg=70.0),
        lie_down=PoseBehaviorModel("lie_down", config, target_deg=45.0),
        walk=AlternatingGaitBehaviorModel("walk", config, amplitude_deg=18.0, delay_s=0.18, default_steps=2),
        run=AlternatingGaitBehaviorModel("run", config, amplitude_deg=24.0, delay_s=0.10, default_steps=3),
        nod=NodBehaviorModel("nod", config),
        tilt_head=TiltHeadBehaviorModel("tilt_head", config),
    )
