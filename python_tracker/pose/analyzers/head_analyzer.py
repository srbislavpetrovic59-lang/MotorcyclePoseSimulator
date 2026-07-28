from pose.geometry import Geometry
from pose.landmarks import PoseLandmark


class HeadAnalyzer:
    """Analyzes rider head orientation."""

    def analyze(self, landmarks):
        head_roll = self._head_roll(landmarks)

        return {
            "head_roll": head_roll,
        }

    def _head_roll(self, landmarks):
        angle = Geometry.line_angle(
            landmarks[PoseLandmark.LEFT_EAR],
            landmarks[PoseLandmark.RIGHT_EAR],
        )

        if angle > 90:
            angle -= 180
        elif angle < -90:
            angle += 180

        return angle