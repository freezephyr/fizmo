from __future__ import annotations

from dataclasses import dataclass

from fizmo.config import RobotConfig
from fizmo.hardware.interfaces import RawImuSensor
from fizmo.models import RawImuSample


class Mpu6050UnavailableError(RuntimeError):
    pass


@dataclass
class Mpu6050RawSensor(RawImuSensor):
    config: RobotConfig

    PWR_MGMT_1 = 0x6B
    ACCEL_XOUT_H = 0x3B

    def __post_init__(self) -> None:
        try:
            import smbus2
        except ImportError as exc:
            raise Mpu6050UnavailableError(
                "MPU6050 support requires smbus2 on the Raspberry Pi."
            ) from exc

        self._bus = smbus2.SMBus(self.config.imu.bus)
        self._address = self.config.imu.i2c_address
        self._bus.write_byte_data(self._address, self.PWR_MGMT_1, 0)

    def read_raw(self) -> RawImuSample:
        accel_x = self._read_word_2c(self.ACCEL_XOUT_H) / 16384.0
        accel_y = self._read_word_2c(self.ACCEL_XOUT_H + 2) / 16384.0
        accel_z = self._read_word_2c(self.ACCEL_XOUT_H + 4) / 16384.0
        gyro_x = self._read_word_2c(self.ACCEL_XOUT_H + 8) / 131.0
        gyro_y = self._read_word_2c(self.ACCEL_XOUT_H + 10) / 131.0
        gyro_z = self._read_word_2c(self.ACCEL_XOUT_H + 12) / 131.0
        return RawImuSample(
            accel_x_g=accel_x,
            accel_y_g=accel_y,
            accel_z_g=accel_z,
            gyro_x_dps=gyro_x,
            gyro_y_dps=gyro_y,
            gyro_z_dps=gyro_z,
        )

    def _read_word_2c(self, register: int) -> int:
        high = self._bus.read_byte_data(self._address, register)
        low = self._bus.read_byte_data(self._address, register + 1)
        value = (high << 8) + low
        if value >= 0x8000:
            return -((65535 - value) + 1)
        return value
