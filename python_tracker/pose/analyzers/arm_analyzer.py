from pose.geometry import Geometry

LEFT_SHOULDER = 11
RIGHT_SHOULDER = 12

LEFT_ELBOW = 13
RIGHT_ELBOW = 14

LEFT_WRIST = 15
RIGHT_WRIST = 16


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
            landmarks[LEFT_SHOULDER],
            landmarks[LEFT_ELBOW],
            landmarks[LEFT_WRIST],
        )

    def _right_elbow_angle(self, landmarks):

        return Geometry.angle(
            landmarks[RIGHT_SHOULDER],
            landmarks[RIGHT_ELBOW],
            landmarks[RIGHT_WRIST],
        )