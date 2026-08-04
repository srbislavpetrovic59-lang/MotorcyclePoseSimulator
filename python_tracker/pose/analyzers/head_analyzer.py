from pickle import TRUE
from pose.geometry import Geometry
from pose.landmarks import PoseLandmark


class HeadAnalyzer:
    """Analyzes rider head orientation."""

    def analyze(self, landmarks):
        head_roll = self._head_roll(landmarks)
        head_yaw = self._head_yaw(landmarks)

        return {
            "head_roll": head_roll,
            "head_yaw_ratio": head_yaw,
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

    def _head_yaw(self, landmarks):
        left_ear = landmarks[PoseLandmark.LEFT_EAR]
        right_ear = landmarks[PoseLandmark.RIGHT_EAR]
        nose = landmarks[PoseLandmark.NOSE]

        left_distance = Geometry.distance(left_ear, nose)
        right_distance = Geometry.distance(nose, right_ear)

        total_distance = left_distance + right_distance

        if total_distance == 0:
            return 0.0

        return (
            left_distance - right_distance
        ) / total_distance

    def is_head_forward(
        self,
        head_roll: float,
        head_yaw_ratio: float,
    ) -> bool:
        return (
            head_roll <= 0.2
            and abs(head_yaw_ratio) <= 0.01
        )