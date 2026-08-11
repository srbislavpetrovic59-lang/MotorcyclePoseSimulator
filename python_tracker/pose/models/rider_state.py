# rider_state.py

import json
from dataclasses import asdict, dataclass


@dataclass(slots=True)
class RiderState:
    timestamp: float = 0.0

    head_roll: float = 0.0
    head_yaw_ratio: float = 0.0

    left_elbow_angle: float = 0.0
    right_elbow_angle: float = 0.

    left_hand_detected: bool = False
    right_hand_detected: bool = False
   
    right_hand_rotation: float = 0.0
    left_hand_rotation: float = 0.0

    throttle_open: bool = False
    throttle_close: bool = False

    clutch_in_friction_zone: bool = False
    clutch_progress: float | None = None

    
    left_knee_angle: float = 0.0
    right_knee_angle: float = 0.0
    
    left_foot_angle: float = 0.0
    right_foot_angle: float = 0.0
    
    torso_angle: float = 0.0
    pose_confidence: float = 0.0

    head_forward: bool = False


    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())