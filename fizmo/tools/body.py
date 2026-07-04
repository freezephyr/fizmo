from __future__ import annotations

from dataclasses import dataclass
from time import sleep

from fizmo.behavior.deterministic import BehaviorRegistry
from fizmo.behavior.models import BehaviorModel, BehaviorPlan
from fizmo.config import RobotConfig
from fizmo.hardware.interfaces import ServoBus
from fizmo.models import Motion, Posture, Safety, ToolResult
from fizmo.servo_math import clamp_servo_deg, logical_leg_angle_to_servo_deg
from fizmo.state.estimator import StateEstimator


@dataclass
class BodyTools:
    servos: ServoBus
    state: StateEstimator
    config: RobotConfig
    behaviors: BehaviorRegistry

    def find_state(self) -> ToolResult:
        current = self.state.read()
        return ToolResult(ok=True, tool="find_state", status="done", state_after=current)

    def halt(self) -> ToolResult:
        before = self.state.read()
        self.servos.stop_all()
        self.state.remember_command("halt", Motion.HALTED)
        after = self.state.read()
        return ToolResult(
            ok=True,
            tool="halt",
            status="done",
            reason="all servo motion stopped",
            state_before=before,
            state_after=after,
        )

    def stand(self) -> ToolResult:
        return self._pose_tool("stand", Posture.STANDING, self.behaviors.stand)

    def sit(self) -> ToolResult:
        return self._pose_tool("sit", Posture.SITTING, self.behaviors.sit)

    def lie_down(self) -> ToolResult:
        return self._pose_tool("lie_down", Posture.LYING_DOWN, self.behaviors.lie_down)

    def walk(self, steps: int = 2) -> ToolResult:
        return self._behavior_tool("walk", self.behaviors.walk, steps=steps, requires_can_move=True)

    def run(self, steps: int = 3) -> ToolResult:
        return self._behavior_tool("run", self.behaviors.run, steps=steps, requires_can_move=True)

    def nod(self) -> ToolResult:
        return self._behavior_tool("nod", self.behaviors.nod)

    def tilt_head(self, direction: str = "left") -> ToolResult:
        return self._behavior_tool("tilt_head", self.behaviors.tilt_head, direction=direction)

    def _pose_tool(self, name: str, posture: Posture, behavior: BehaviorModel) -> ToolResult:
        before = self.state.read()
        if before.safety == Safety.HALT_REQUIRED or before.safety == Safety.FAULT:
            return ToolResult(
                ok=False,
                tool=name,
                status="rejected",
                reason=f"unsafe state: {before.safety.value}",
                state_before=before,
                state_after=before,
            )

        result = self._execute_behavior(name, behavior.plan(before))
        self.state.set_posture_hint(posture)
        after = self.state.read()
        return ToolResult(
            ok=result.ok,
            tool=name,
            status=result.status,
            reason=result.reason,
            state_before=before,
            state_after=after,
            data=result.data,
        )

    def _behavior_tool(
        self,
        name: str,
        behavior: BehaviorModel,
        requires_can_move: bool = False,
        **kwargs: object,
    ) -> ToolResult:
        before = self.state.read()
        if requires_can_move and not before.can_move:
            return ToolResult(
                ok=False,
                tool=name,
                status="rejected",
                reason=f"robot cannot move: safety={before.safety.value}, stability={before.stability.value}",
                state_before=before,
                state_after=before,
            )
        if before.safety not in (Safety.OK, Safety.CAUTION):
            return ToolResult(
                ok=False,
                tool=name,
                status="rejected",
                reason=f"unsafe state: {before.safety.value}",
                state_before=before,
                state_after=before,
            )

        plan = behavior.plan(before, **kwargs)
        if not plan.expected_done:
            return ToolResult(
                ok=False,
                tool=name,
                status="rejected",
                reason=str(plan.metadata.get("error", "behavior model could not produce a plan")),
                state_before=before,
                state_after=before,
                data=plan.metadata,
            )
        result = self._execute_behavior(name, plan)
        after = self.state.read()
        return ToolResult(
            ok=result.ok,
            tool=name,
            status=result.status,
            reason=result.reason,
            state_before=before,
            state_after=after,
            data=result.data,
        )

    def _execute_behavior(self, name: str, plan: BehaviorPlan) -> ToolResult:
        self.state.remember_command(name, Motion.MOVING)
        for frame in plan.frames:
            for servo_name, angle_deg in frame.targets_deg.items():
                self.servos.set_angle(servo_name, self._resolve_frame_angle(frame.angle_space, servo_name, angle_deg))
            if frame.delay_s > 0:
                sleep(frame.delay_s)

        self.state.remember_command(name, Motion.IDLE)
        return ToolResult(
            ok=True,
            tool=name,
            status="done",
            data={"confidence": plan.confidence, **plan.metadata},
        )

    def _clamp_servo_angle(self, servo_name: str, requested_deg: float) -> float:
        servo = next(item for item in self.config.servos if item.name == servo_name)
        return clamp_servo_deg(servo, requested_deg)

    def _resolve_frame_angle(self, angle_space: str, servo_name: str, angle_deg: float) -> float:
        servo = next(item for item in self.config.servos if item.name == servo_name)
        if angle_space == "logical":
            return logical_leg_angle_to_servo_deg(servo, angle_deg)
        if angle_space == "servo":
            return clamp_servo_deg(servo, angle_deg)
        raise ValueError(f"unknown servo frame angle space: {angle_space}")

    def _center_servos(self) -> None:
        for servo in self.config.servos:
            self.servos.set_angle(servo.name, self._clamp_servo_angle(servo.name, servo.neutral_deg))
