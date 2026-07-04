from __future__ import annotations

from dataclasses import dataclass

from fizmo.config import RobotConfig, ServoConfig
from fizmo.hardware.interfaces import ServoBus


class Pca9685UnavailableError(RuntimeError):
    pass


@dataclass
class Pca9685ServoBus(ServoBus):
    config: RobotConfig

    def __post_init__(self) -> None:
        self._last_angles: dict[str, float] = {}
        try:
            import board
            from adafruit_pca9685 import PCA9685
        except ImportError as exc:
            raise Pca9685UnavailableError(
                "PCA9685 support requires Raspberry Pi I2C libraries: "
                "adafruit-circuitpython-pca9685 and board."
            ) from exc

        i2c = board.I2C()
        self._pca = PCA9685(i2c, address=self.config.servo_driver.i2c_address)
        self._pca.frequency = self.config.servo_driver.frequency_hz

    def set_angle(self, servo_name: str, angle_deg: float) -> None:
        servo = self._get_servo(servo_name)
        clamped = max(servo.min_deg, min(servo.max_deg, angle_deg))
        pulse_us = self._angle_to_pulse_us(clamped)
        duty_cycle = self._pulse_us_to_duty_cycle(pulse_us)
        self._pca.channels[servo.channel].duty_cycle = duty_cycle
        self._last_angles[servo.name] = clamped

    def stop_all(self) -> None:
        for servo in self.config.servos:
            self._pca.channels[servo.channel].duty_cycle = 0

    def get_angles(self) -> dict[str, float]:
        return dict(self._last_angles)

    def _get_servo(self, servo_name: str) -> ServoConfig:
        return next(servo for servo in self.config.servos if servo.name == servo_name)

    def _angle_to_pulse_us(self, angle_deg: float) -> float:
        driver = self.config.servo_driver
        span = driver.max_pulse_us - driver.min_pulse_us
        normalized = angle_deg / 180.0
        return driver.min_pulse_us + normalized * span

    def _pulse_us_to_duty_cycle(self, pulse_us: float) -> int:
        period_us = 1_000_000.0 / self.config.servo_driver.frequency_hz
        duty_fraction = pulse_us / period_us
        return int(max(0.0, min(1.0, duty_fraction)) * 0xFFFF)
