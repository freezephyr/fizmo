from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from time import time
from typing import Any


class Posture(str, Enum):
    UNKNOWN = "unknown"
    STANDING = "standing"
    SITTING = "sitting"
    LYING_DOWN = "lying_down"
    FALLEN = "fallen"


class Motion(str, Enum):
    IDLE = "idle"
    MOVING = "moving"
    RECOVERING = "recovering"
    HALTED = "halted"


class Stability(str, Enum):
    UNKNOWN = "unknown"
    STABLE = "stable"
    LEANING = "leaning"
    TIPPED = "tipped"
    FALLEN = "fallen"


class Safety(str, Enum):
    OK = "ok"
    CAUTION = "caution"
    HALT_REQUIRED = "halt_required"
    FAULT = "fault"


@dataclass(frozen=True)
class ImuReading:
    roll_deg: float = 0.0
    pitch_deg: float = 0.0
    yaw_rate_dps: float = 0.0
    accel_magnitude_g: float = 1.0
    timestamp: float = field(default_factory=time)


@dataclass(frozen=True)
class RawImuSample:
    accel_x_g: float = 0.0
    accel_y_g: float = 0.0
    accel_z_g: float = 1.0
    gyro_x_dps: float = 0.0
    gyro_y_dps: float = 0.0
    gyro_z_dps: float = 0.0
    timestamp: float = field(default_factory=time)


@dataclass(frozen=True)
class RobotState:
    posture: Posture = Posture.UNKNOWN
    motion: Motion = Motion.IDLE
    stability: Stability = Stability.UNKNOWN
    safety: Safety = Safety.OK
    imu: ImuReading = field(default_factory=ImuReading)
    servo_angles_deg: dict[str, float] = field(default_factory=dict)
    confidence: float = 0.0
    last_command: str | None = None
    note: str | None = None
    timestamp: float = field(default_factory=time)

    @property
    def can_move(self) -> bool:
        return self.safety == Safety.OK and self.stability == Stability.STABLE


@dataclass(frozen=True)
class ToolResult:
    ok: bool
    tool: str
    status: str
    reason: str | None = None
    state_before: RobotState | None = None
    state_after: RobotState | None = None
    data: dict[str, Any] = field(default_factory=dict)
