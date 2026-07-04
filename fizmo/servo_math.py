from __future__ import annotations

from fizmo.config import ServoConfig


def logical_leg_angle_to_servo_deg(servo: ServoConfig, logical_angle_deg: float) -> float:
    direction = -1.0 if servo.reversed else 1.0
    requested = servo.logical_zero_deg + direction * servo.logical_scale * logical_angle_deg
    return clamp_servo_deg(servo, requested)


def clamp_servo_deg(servo: ServoConfig, servo_angle_deg: float) -> float:
    return max(servo.min_deg, min(servo.max_deg, servo_angle_deg))
