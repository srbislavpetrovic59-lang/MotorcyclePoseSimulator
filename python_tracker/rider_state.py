#rider_state.py
from dataclasses import dataclass


@dataclass
class RiderState:
    left_elbow_angle: float = 0.0
    right_elbow_angle: float = 0.0
    pose_confidence: float = 0.0