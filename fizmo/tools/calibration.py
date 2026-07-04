from __future__ import annotations

from dataclasses import dataclass

from fizmo.config import RobotConfig, ServoConfig
from fizmo.hardware.interfaces import ServoBus
from fizmo.models import ToolResult
from fizmo.servo_math import clamp_servo_deg
from fizmo.state.estimator import StateEstimator


@dataclass
class CalibrationTools:
    servos: ServoBus
    state: StateEstimator
    config: RobotConfig

    def set_servo_angle(self, servo_name: str, angle_deg: float) -> ToolResult:
        before = self.state.read()
        servo = self._get_servo(servo_name)
        angle = self._clamp(servo, angle_deg)
        self.servos.set_angle(servo.name, angle)
        self.state.remember_command(f"calibrate:{servo.name}:{angle:.1f}")
        after = self.state.read()
        return ToolResult(
            ok=True,
            tool="set_servo_angle",
            status="done",
            state_before=before,
            state_after=after,
            data={"servo": servo.name, "requested_deg": angle_deg, "sent_deg": angle},
        )

    def center_all(self) -> ToolResult:
        before = self.state.read()
        for servo in self.config.servos:
            self.servos.set_angle(servo.name, servo.neutral_deg)
        self.state.remember_command("calibrate:center_all")
        after = self.state.read()
        return ToolResult(ok=True, tool="center_all", status="done", state_before=before, state_after=after)

    def stop_all(self) -> ToolResult:
        before = self.state.read()
        self.servos.stop_all()
        self.state.remember_command("calibrate:stop_all")
        after = self.state.read()
        return ToolResult(ok=True, tool="stop_all", status="done", state_before=before, state_after=after)

    def _get_servo(self, servo_name: str) -> ServoConfig:
        return next(servo for servo in self.config.servos if servo.name == servo_name)

    @staticmethod
    def _clamp(servo: ServoConfig, angle_deg: float) -> float:
        return clamp_servo_deg(servo, angle_deg)
