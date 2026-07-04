from __future__ import annotations

from dataclasses import dataclass

from fizmo.config import RobotConfig
from fizmo.hardware.interfaces import ImuSensor, ServoBus
from fizmo.models import ImuReading, Motion, Posture, RobotState, Safety, Stability


@dataclass
class StateEstimator:
    imu: ImuSensor
    config: RobotConfig
    servos: ServoBus | None = None
    posture_hint: Posture = Posture.UNKNOWN
    motion: Motion = Motion.IDLE
    last_command: str | None = None

    def read(self) -> RobotState:
        imu = self.imu.read()
        stability, safety = self._classify_stability(imu)
        posture = self._classify_posture(stability)
        confidence = 0.8 if stability != Stability.UNKNOWN else 0.2
        return RobotState(
            posture=posture,
            motion=self.motion,
            stability=stability,
            safety=safety,
            imu=imu,
            servo_angles_deg=self.servos.get_angles() if self.servos else {},
            confidence=confidence,
            last_command=self.last_command,
        )

    def remember_command(self, command: str, motion: Motion | None = None) -> None:
        self.last_command = command
        if motion is not None:
            self.motion = motion

    def set_posture_hint(self, posture: Posture) -> None:
        self.posture_hint = posture

    def _classify_stability(self, imu: ImuReading) -> tuple[Stability, Safety]:
        max_tilt = max(abs(imu.roll_deg), abs(imu.pitch_deg))
        if max_tilt >= self.config.fallen_tilt_deg:
            return Stability.FALLEN, Safety.HALT_REQUIRED
        if max_tilt >= self.config.caution_tilt_deg:
            return Stability.TIPPED, Safety.HALT_REQUIRED
        if max_tilt >= self.config.stable_tilt_deg:
            return Stability.LEANING, Safety.CAUTION
        return Stability.STABLE, Safety.OK

    def _classify_posture(self, stability: Stability) -> Posture:
        if stability == Stability.FALLEN:
            return Posture.FALLEN
        if self.posture_hint != Posture.UNKNOWN:
            return self.posture_hint
        if stability == Stability.STABLE:
            return Posture.STANDING
        return Posture.UNKNOWN
