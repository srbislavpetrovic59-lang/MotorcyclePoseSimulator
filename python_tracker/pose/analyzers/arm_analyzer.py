from pose.geometry import Geometry
from pose.landmarks import PoseLandmark


class ArmAnalyzer:


    def analyze(self, landmarks):

        left_angle = self._left_elbow_angle(landmarks)
        right_angle = self._right_elbow_angle(landmarks)

        return {
            "left_elbow_angle": left_angle,
            "right_elbow_angle": right_angle,

            "left_arm_extended": left_angle > 165,
            "right_arm_extended": right_angle > 165,

            "arm_symmetry": round(
                max(0.0, 100.0 - abs(left_angle - right_angle)),
                1,
            ),
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

    def _left_arm_extended(self, landmarks):

        return self._left_elbow_angle(landmarks) > 165


    def _right_arm_extended(self, landmarks):

        return self._right_elbow_angle(landmarks) > 165

    def _arm_symmetry(self, landmarks):

        left = self._left_elbow_angle(landmarks)
        right = self._right_elbow_angle(landmarks)

        difference = abs(left - right)

        return round(100 - difference, 1)

 