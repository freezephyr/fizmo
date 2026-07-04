from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from time import time

from fizmo.models import ImuReading, RawImuSample


@dataclass(frozen=True)
class CameraFrame:
    path: str | None = None
    width: int | None = None
    height: int | None = None
    timestamp: float = field(default_factory=time)


@dataclass(frozen=True)
class AudioSample:
    pcm: bytes
    sample_rate_hz: int
    channels: int
    sample_width_bytes: int
    duration_s: float
    rms: float
    timestamp: float = field(default_factory=time)

    @property
    def has_signal(self) -> bool:
        return self.rms > 0.0


class ServoBus(ABC):
    @abstractmethod
    def set_angle(self, servo_name: str, angle_deg: float) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop_all(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_angles(self) -> dict[str, float]:
        raise NotImplementedError


class ImuSensor(ABC):
    @abstractmethod
    def read(self) -> ImuReading:
        raise NotImplementedError


class RawImuSensor(ABC):
    @abstractmethod
    def read_raw(self) -> RawImuSample:
        raise NotImplementedError


class Display(ABC):
    @abstractmethod
    def show_face(self, expression: str, text: str | None = None) -> None:
        raise NotImplementedError


class Speaker(ABC):
    @abstractmethod
    def speak(self, text: str) -> None:
        raise NotImplementedError


class Camera(ABC):
    @abstractmethod
    def capture(self) -> CameraFrame:
        raise NotImplementedError


class Microphone(ABC):
    @abstractmethod
    def listen(self, duration_s: float | None = None) -> AudioSample:
        raise NotImplementedError
