from __future__ import annotations

from dataclasses import dataclass, field

from fizmo.hardware.interfaces import AudioSample, Camera, CameraFrame, Display, ImuSensor, Microphone, RawImuSensor, ServoBus, Speaker
from fizmo.models import ImuReading, RawImuSample


@dataclass
class MockServoBus(ServoBus):
    angles: dict[str, float] = field(default_factory=dict)
    stopped: bool = True

    def set_angle(self, servo_name: str, angle_deg: float) -> None:
        self.angles[servo_name] = angle_deg
        self.stopped = False

    def stop_all(self) -> None:
        self.stopped = True

    def get_angles(self) -> dict[str, float]:
        return dict(self.angles)


@dataclass
class MockImuSensor(ImuSensor, RawImuSensor):
    reading: ImuReading = field(default_factory=ImuReading)
    raw_sample: RawImuSample = field(default_factory=RawImuSample)

    def read(self) -> ImuReading:
        return self.reading

    def read_raw(self) -> RawImuSample:
        return self.raw_sample


@dataclass
class MockDisplay(Display):
    expression: str = "idle"
    text: str | None = None

    def show_face(self, expression: str, text: str | None = None) -> None:
        self.expression = expression
        self.text = text


class MockSpeaker(Speaker):
    def __init__(self) -> None:
        self.last_text: str | None = None

    def speak(self, text: str) -> None:
        self.last_text = text


@dataclass
class MockCamera(Camera):
    frame: CameraFrame = field(default_factory=CameraFrame)

    def capture(self) -> CameraFrame:
        return self.frame


@dataclass
class MockMicrophone(Microphone):
    sample_rate_hz: int = 16000
    channels: int = 1
    sample_width_bytes: int = 2
    rms: float = 0.0

    def listen(self, duration_s: float | None = None) -> AudioSample:
        duration = 0.1 if duration_s is None else duration_s
        frame_count = max(1, int(self.sample_rate_hz * duration))
        pcm = b"\x00" * frame_count * self.channels * self.sample_width_bytes
        return AudioSample(
            pcm=pcm,
            sample_rate_hz=self.sample_rate_hz,
            channels=self.channels,
            sample_width_bytes=self.sample_width_bytes,
            duration_s=duration,
            rms=self.rms,
        )
