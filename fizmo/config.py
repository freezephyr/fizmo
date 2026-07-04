from __future__ import annotations

from configparser import ConfigParser
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ServoConfig:
    name: str
    channel: int
    neutral_deg: float = 90.0
    logical_zero_deg: float = 0.0
    logical_scale: float = 1.0
    min_deg: float = 0.0
    max_deg: float = 180.0
    reversed: bool = False


@dataclass(frozen=True)
class ServoDriverConfig:
    kind: str = "pca9685"
    i2c_address: int = 0x40
    frequency_hz: int = 50
    min_pulse_us: int = 500
    max_pulse_us: int = 2500


@dataclass(frozen=True)
class ImuConfig:
    kind: str = "mpu6050"
    i2c_address: int = 0x68
    bus: int = 1


@dataclass(frozen=True)
class DisplayConfig:
    kind: str = "pirate_audio"
    width: int = 240
    height: int = 240


@dataclass(frozen=True)
class CameraConfig:
    kind: str = "raspberry_pi_camera"
    megapixels: int = 5


@dataclass(frozen=True)
class AudioConfig:
    microphone_kind: str = "usb_alsa"
    input_device: str = "default"
    sample_rate_hz: int = 16000
    channels: int = 1
    sample_width_bytes: int = 2
    listen_seconds: float = 3.0
    speech_rms_threshold: float = 0.01


@dataclass(frozen=True)
class SpeechToTextConfig:
    provider: str = "mock"
    model: str = "whisper"
    language: str = "en"


@dataclass(frozen=True)
class TextModelConfig:
    provider: str = "mock"
    model: str = "mock-text"
    system_prompt: str = "You are Fizmo, a small helpful robot."


@dataclass(frozen=True)
class LoggingConfig:
    enabled: bool = True
    directory: str = "logs/behavior"
    max_files: int = 20
    max_total_mb: float = 250.0


@dataclass(frozen=True)
class AgentConfig:
    wake_word: str = "Fiz"


@dataclass(frozen=True)
class RobotConfig:
    servos: tuple[ServoConfig, ...] = field(
        default_factory=lambda: (
            ServoConfig("front_left", 0),
            ServoConfig("front_right", 1),
            ServoConfig("rear_left", 2),
            ServoConfig("rear_right", 3),
        )
    )
    servo_driver: ServoDriverConfig = field(default_factory=ServoDriverConfig)
    imu: ImuConfig = field(default_factory=ImuConfig)
    display: DisplayConfig = field(default_factory=DisplayConfig)
    camera: CameraConfig = field(default_factory=CameraConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    speech_to_text: SpeechToTextConfig = field(default_factory=SpeechToTextConfig)
    text_model: TextModelConfig = field(default_factory=TextModelConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    leg_length_mm: float = 56.0
    stable_tilt_deg: float = 12.0
    caution_tilt_deg: float = 25.0
    fallen_tilt_deg: float = 45.0


DEFAULT_CONFIG = RobotConfig()


def load_robot_config(path: str | Path = "config/robot.ini") -> RobotConfig:
    config_path = Path(path)
    if not config_path.exists():
        return DEFAULT_CONFIG

    parser = ConfigParser()
    parser.read(config_path)

    servos = []
    for section in parser.sections():
        if not section.startswith("servo."):
            continue
        name = section.removeprefix("servo.")
        servos.append(
            ServoConfig(
                name=name,
                channel=parser.getint(section, "channel"),
                neutral_deg=parser.getfloat(section, "neutral_deg", fallback=90.0),
                logical_zero_deg=parser.getfloat(section, "logical_zero_deg", fallback=0.0),
                logical_scale=parser.getfloat(section, "logical_scale", fallback=1.0),
                min_deg=parser.getfloat(section, "min_deg", fallback=0.0),
                max_deg=parser.getfloat(section, "max_deg", fallback=180.0),
                reversed=parser.getboolean(section, "reversed", fallback=False),
            )
        )

    default = DEFAULT_CONFIG
    return RobotConfig(
        servos=tuple(servos) if servos else default.servos,
        servo_driver=ServoDriverConfig(
            kind=parser.get("servo_driver", "kind", fallback=default.servo_driver.kind),
            i2c_address=_parse_int(parser.get("servo_driver", "i2c_address", fallback=str(default.servo_driver.i2c_address))),
            frequency_hz=parser.getint("servo_driver", "frequency_hz", fallback=default.servo_driver.frequency_hz),
            min_pulse_us=parser.getint("servo_driver", "min_pulse_us", fallback=default.servo_driver.min_pulse_us),
            max_pulse_us=parser.getint("servo_driver", "max_pulse_us", fallback=default.servo_driver.max_pulse_us),
        ),
        imu=ImuConfig(
            kind=parser.get("imu", "kind", fallback=default.imu.kind),
            i2c_address=_parse_int(parser.get("imu", "i2c_address", fallback=str(default.imu.i2c_address))),
            bus=parser.getint("imu", "bus", fallback=default.imu.bus),
        ),
        display=DisplayConfig(
            kind=parser.get("display", "kind", fallback=default.display.kind),
            width=parser.getint("display", "width", fallback=default.display.width),
            height=parser.getint("display", "height", fallback=default.display.height),
        ),
        camera=CameraConfig(
            kind=parser.get("camera", "kind", fallback=default.camera.kind),
            megapixels=parser.getint("camera", "megapixels", fallback=default.camera.megapixels),
        ),
        audio=AudioConfig(
            microphone_kind=parser.get("audio", "microphone_kind", fallback=default.audio.microphone_kind),
            input_device=parser.get("audio", "input_device", fallback=default.audio.input_device),
            sample_rate_hz=parser.getint("audio", "sample_rate_hz", fallback=default.audio.sample_rate_hz),
            channels=parser.getint("audio", "channels", fallback=default.audio.channels),
            sample_width_bytes=parser.getint("audio", "sample_width_bytes", fallback=default.audio.sample_width_bytes),
            listen_seconds=parser.getfloat("audio", "listen_seconds", fallback=default.audio.listen_seconds),
            speech_rms_threshold=parser.getfloat("audio", "speech_rms_threshold", fallback=default.audio.speech_rms_threshold),
        ),
        speech_to_text=SpeechToTextConfig(
            provider=parser.get("speech_to_text", "provider", fallback=default.speech_to_text.provider),
            model=parser.get("speech_to_text", "model", fallback=default.speech_to_text.model),
            language=parser.get("speech_to_text", "language", fallback=default.speech_to_text.language),
        ),
        text_model=TextModelConfig(
            provider=parser.get("text_model", "provider", fallback=default.text_model.provider),
            model=parser.get("text_model", "model", fallback=default.text_model.model),
            system_prompt=parser.get("text_model", "system_prompt", fallback=default.text_model.system_prompt),
        ),
        logging=LoggingConfig(
            enabled=parser.getboolean("logging", "enabled", fallback=default.logging.enabled),
            directory=parser.get("logging", "directory", fallback=default.logging.directory),
            max_files=parser.getint("logging", "max_files", fallback=default.logging.max_files),
            max_total_mb=parser.getfloat("logging", "max_total_mb", fallback=default.logging.max_total_mb),
        ),
        agent=AgentConfig(
            wake_word=parser.get("agent", "wake_word", fallback=default.agent.wake_word),
        ),
        leg_length_mm=parser.getfloat("robot", "leg_length_mm", fallback=default.leg_length_mm),
        stable_tilt_deg=parser.getfloat("robot", "stable_tilt_deg", fallback=default.stable_tilt_deg),
        caution_tilt_deg=parser.getfloat("robot", "caution_tilt_deg", fallback=default.caution_tilt_deg),
        fallen_tilt_deg=parser.getfloat("robot", "fallen_tilt_deg", fallback=default.fallen_tilt_deg),
    )


def _parse_int(value: str) -> int:
    return int(value, 0)
