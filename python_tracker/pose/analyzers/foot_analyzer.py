from pose.geometry import Geometry
from pose.landmarks import PoseLandmark


class FootAnalyzer:

    def analyze(self, landmarks):
        left_knee_angle = self._left_knee_angle(landmarks)
        right_knee_angle = self._right_knee_angle(landmarks)

        left_foot_angle = self._left_foot_angle(landmarks)
        right_foot_angle = self._right_foot_angle(landmarks)
        
        return {
            "left_knee_angle": left_knee_angle,
            "right_knee_angle": right_knee_angle,
            "left_foot_angle": left_foot_angle,
            "right_foot_angle": right_foot_angle,

            "left_leg_extended": left_knee_angle > 165,
            "right_leg_extended": right_knee_angle > 165,

            "leg_symmetry": round(
                max(0.0, 100.0 - abs(left_knee_angle - right_knee_angle)),
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
    def _left_foot_angle(self, landmarks):
        return Geometry.angle(
            landmarks[PoseLandmark.LEFT_KNEE],
            landmarks[PoseLandmark.LEFT_ANKLE],
            landmarks[PoseLandmark.LEFT_FOOT_INDEX],
        )

    def _right_foot_angle(self, landmarks):
        return Geometry.angle(
            landmarks[PoseLandmark.RIGHT_KNEE],
            landmarks[PoseLandmark.RIGHT_ANKLE],
            landmarks[PoseLandmark.RIGHT_FOOT_INDEX],
        )