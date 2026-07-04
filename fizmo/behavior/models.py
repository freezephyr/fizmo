from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from fizmo.models import RobotState


@dataclass(frozen=True)
class ServoFrame:
    targets_deg: dict[str, float]
    delay_s: float = 0.0
    angle_space: str = "logical"


@dataclass(frozen=True)
class BehaviorPlan:
    frames: tuple[ServoFrame, ...]
    expected_done: bool = True
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


class BehaviorModel(ABC):
    name: str

    @abstractmethod
    def plan(self, state: RobotState, **kwargs: Any) -> BehaviorPlan:
        raise NotImplementedError
