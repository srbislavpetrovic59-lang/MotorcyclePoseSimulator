from enum import Enum


class RidingPhase(Enum):
    IDLE = "IDLE"
    ACCELERATION = "ACCELERATION"
    BRAKING = "BRAKING"
    CORNERING = "CORNERING"
    EXIT = "EXIT"