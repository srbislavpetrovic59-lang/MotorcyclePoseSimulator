from pose.geometry import Geometry
from pose.landmarks import PoseLandmark

class ArmAnalyzer:

    def analyze(self, landmarks):

        left_angle = self._left_elbow_angle(landmarks)
        right_angle = self._right_elbow_angle(landmarks)

        return {
            "left_elbow_angle": left_angle,
            "right_elbow_angle": right_angle,
        }

    def _left_elbow_angle(self, landmarks):

        return Geometry.angle(
            landmarks[PoseLandmark.LEFT_SHOULDER],
            landmarks[PoseLandmark.LEFT_ELBOW],
            landmarks[PoseLandmark.LEFT_WRIST],
        )

    def _right_elbow_angle(self, landmarks):

        return Geometry.angle(
            landmarks[PoseLandmark.RIGHT_SHOULDER],
            landmarks[PoseLandmark.RIGHT_ELBOW],
            landmarks[PoseLandmark.RIGHT_WRIST],
       )