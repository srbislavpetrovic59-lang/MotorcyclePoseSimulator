from dataclasses import dataclass
from enum import Enum, auto


class RiderEventType(Enum):
    RIDE_STARTED = auto()
    RIDE_STOPPED = auto()


@dataclass(frozen=True)
class RiderEvent:
    type: RiderEventType
    timestamp: float