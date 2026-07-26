# rider_state.py

import json
from dataclasses import asdict, dataclass


@dataclass(slots=True)
class RiderState:
    left_elbow_angle: float = 0.0
    right_elbow_angle: float = 0.0
    pose_confidence: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())