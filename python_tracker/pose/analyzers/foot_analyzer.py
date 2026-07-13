from pose.geometry import Geometry
from pose.landmarks import PoseLandmark


class FootAnalyzer:

    def analyze(self, landmarks):
        left_angle = self._left_knee_angle(landmarks)
        right_angle = self._right_knee_angle(landmarks)

        return {
            "left_knee_angle": left_angle,
            "right_knee_angle": right_angle,

            "left_leg_extended": left_angle > 165,
            "right_leg_extended": right_angle > 165,

            "leg_symmetry": round(
                max(0.0, 100.0 - abs(left_angle - right_angle)),
                1,
            ),
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