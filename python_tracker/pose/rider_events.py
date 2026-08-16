from dataclasses import dataclass
from enum import Enum, auto


class RiderEventType(Enum):
    POSE_ACQUIRED = auto()
    POSE_LOST = auto()
    
    RIDE_STARTED = auto()
    RIDE_STOPPED = auto()

    LEFT_HAND_DETECTED = auto()
    LEFT_HAND_LOST = auto

    RIGHT_HAND_DETECTED = auto()
    RIGHT_HAND_LOST = auto()

    LOOKING_AHEAD = auto()
    LOOKING_AWAY = auto()

    THROTTLE_OPENED = auto()
    THROTTLE_CLOSED = auto()
   
    CLUTCH_FRICTION_ZONE_REACHED = auto()
    CLUTCH_RELEASED_FROM_FRICTION_ZONE = auto()
    CLUTCH_PULLED_FROM_FRICTION_ZONE = auto()
    
    FRONT_BRAKE_APPLIED = auto()
    FRONT_BRAKE_RELEASED = auto()

@dataclass(frozen=True)
class RiderEvent:
    type: RiderEventType
    timestamp: float