from __future__ import annotations

import argparse

from fizmo.config import load_robot_config
from fizmo.hardware.mock import MockImuSensor, MockServoBus
from fizmo.hardware.pca9685 import Pca9685ServoBus
from fizmo.state.estimator import StateEstimator
from fizmo.tools.calibration import CalibrationTools


def build_tools(use_real_hardware: bool) -> CalibrationTools:
    config = load_robot_config()
    imu = MockImuSensor()
    servos = Pca9685ServoBus(config) if use_real_hardware else MockServoBus()
    state = StateEstimator(imu=imu, config=config, servos=servos)
    return CalibrationTools(servos=servos, state=state, config=config)


def main() -> None:
    parser = argparse.ArgumentParser(description="Safely move fizmo servos for calibration.")
    config = load_robot_config()
    parser.add_argument("--real", action="store_true", help="Use the real PCA9685 hardware adapter.")
    parser.add_argument("--servo", choices=[servo.name for servo in config.servos])
    parser.add_argument("--angle", type=float)
    parser.add_argument("--center-all", action="store_true")
    parser.add_argument("--stop-all", action="store_true")
    args = parser.parse_args()

    tools = build_tools(use_real_hardware=args.real)

    if args.center_all:
        result = tools.center_all()
    elif args.stop_all:
        result = tools.stop_all()
    elif args.servo and args.angle is not None:
        result = tools.set_servo_angle(args.servo, args.angle)
    else:
        parser.error("Choose --center-all, --stop-all, or --servo NAME --angle DEG.")

    print(result)


if __name__ == "__main__":
    main()
