from __future__ import annotations

import argparse
from time import sleep

from fizmo.config import load_robot_config
from fizmo.hardware.mock import MockImuSensor
from fizmo.hardware.mpu6050 import Mpu6050RawSensor
from fizmo.models import RawImuSample
from fizmo.state.imu_filter import FilteredImuSensor


def main() -> None:
    parser = argparse.ArgumentParser(description="Read fizmo IMU state.")
    parser.add_argument("--real", action="store_true", help="Use real MPU6050 hardware.")
    parser.add_argument("--samples", type=int, default=5)
    parser.add_argument("--delay", type=float, default=0.1)
    parser.add_argument("--mock-roll", type=float, default=0.0)
    parser.add_argument("--mock-pitch", type=float, default=0.0)
    args = parser.parse_args()

    config = load_robot_config()
    if args.real:
        raw_sensor = Mpu6050RawSensor(config)
    else:
        raw_sensor = MockImuSensor(raw_sample=_mock_sample(args.mock_roll, args.mock_pitch))

    imu = FilteredImuSensor(raw_sensor)
    for _ in range(max(1, args.samples)):
        print(imu.read())
        sleep(args.delay)


def _mock_sample(roll_deg: float, pitch_deg: float) -> RawImuSample:
    # Approximate gravity vector for simple CLI smoke tests.
    from math import radians, sin, cos

    roll = radians(roll_deg)
    pitch = radians(pitch_deg)
    return RawImuSample(
        accel_x_g=-sin(pitch),
        accel_y_g=sin(roll) * cos(pitch),
        accel_z_g=cos(roll) * cos(pitch),
    )


if __name__ == "__main__":
    main()
