from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from math import atan2, degrees, sqrt

from fizmo.models import ImuReading, RawImuSample


@dataclass
class ImuStreamFilter:
    window_size: int = 5
    samples: deque[RawImuSample] = field(default_factory=deque)

    def update(self, sample: RawImuSample) -> ImuReading:
        self.samples.append(sample)
        while len(self.samples) > self.window_size:
            self.samples.popleft()

        accel_x = self._avg("accel_x_g")
        accel_y = self._avg("accel_y_g")
        accel_z = self._avg("accel_z_g")
        gyro_z = self._avg("gyro_z_dps")

        roll = degrees(atan2(accel_y, accel_z))
        pitch = degrees(atan2(-accel_x, sqrt(accel_y * accel_y + accel_z * accel_z)))
        accel_mag = sqrt(accel_x * accel_x + accel_y * accel_y + accel_z * accel_z)

        return ImuReading(
            roll_deg=roll,
            pitch_deg=pitch,
            yaw_rate_dps=gyro_z,
            accel_magnitude_g=accel_mag,
            timestamp=sample.timestamp,
        )

    def _avg(self, attr: str) -> float:
        if not self.samples:
            return 0.0
        return sum(getattr(sample, attr) for sample in self.samples) / len(self.samples)


@dataclass
class FilteredImuSensor:
    raw_sensor: object
    stream_filter: ImuStreamFilter = field(default_factory=ImuStreamFilter)

    def read(self) -> ImuReading:
        sample = self.raw_sensor.read_raw()
        return self.stream_filter.update(sample)
