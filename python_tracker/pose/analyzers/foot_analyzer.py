from pose.geometry import Geometry
from pose.landmarks import PoseLandmark


class FootAnalyzer:

    def analyze(self, landmarks):
        return {
            "left_knee_angle": self._left_knee_angle(landmarks),
            "right_knee_angle": self._right_knee_angle(landmarks),
        }

    def _left_knee_angle(self, landmarks):
        return Geometry.angle(
            landmarks[PoseLandmark.LEFT_HIP],
            landmarks[PoseLandmark.LEFT_KNEE],
            landmarks[PoseLandmark.LEFT_ANKLE],
        )

    def _right_knee_angle(self, landmarks):
        return Geometry.angle(
            landmarks[PoseLandmark.RIGHT_HIP],
            landmarks[PoseLandmark.RIGHT_KNEE],
            landmarks[PoseLandmark.RIGHT_ANKLE],
        )