from pose.geometry import Geometry
from pose.landmarks import PoseLandmark


class BodyAnalyzer:

    def analyze(self, landmarks):

        return {
            "torso_angle": self._torso_angle(landmarks),
            "shoulder_tilt": self._shoulder_tilt(landmarks),
        }

    def _torso_angle(self, landmarks):
        shoulders = Geometry.midpoint(
            landmarks[PoseLandmark.LEFT_SHOULDER],
            landmarks[PoseLandmark.RIGHT_SHOULDER],
        )

        hips = Geometry.midpoint(
            landmarks[PoseLandmark.LEFT_HIP],
            landmarks[PoseLandmark.RIGHT_HIP],
        )

        return Geometry.line_angle(
            shoulders,
            hips,
        )

    def _shoulder_tilt(self, landmarks):
        return Geometry.line_angle(
            landmarks[PoseLandmark.LEFT_SHOULDER],
            landmarks[PoseLandmark.RIGHT_SHOULDER],
        )