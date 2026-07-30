from dataclasses import dataclass
from typing import Any


@dataclass
class FrameAnalysis:
    pose_landmarks: Any
    hand_landmarks: Any