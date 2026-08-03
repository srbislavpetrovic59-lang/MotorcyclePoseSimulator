from dataclasses import dataclass
from enum import Enum, auto


class RiderEventType(Enum):
    POSE_ACQUIRED = auto()
    POSE_LOST = auto()
    
    RIDE_STARTED = auto()
    RIDE_STOPPED = auto()

    LEFT_HAND_DETECTED = auto()
    LEFT_HAND_LOST = auto()
    

@dataclass(frozen=True)
class RiderEvent:
    type: RiderEventType
    timestamp: float