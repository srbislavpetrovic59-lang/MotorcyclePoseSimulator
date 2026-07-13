from pose.geometry import Geometry
from pose.landmarks import PoseLandmark

UPRIGHT_MIN_ANGLE = 85.0
UPRIGHT_MAX_ANGLE = 95.0
FORWARD_LEAN_MIN_ANGLE = 100.0
SHOULDER_LEVEL_TOLERANCE = 5.0


class BodyAnalyzer:

    def analyze(self, landmarks):
        torso_angle = self._torso_angle(landmarks)
        shoulder_tilt = self._shoulder_tilt(landmarks)

        return {
            "torso_angle": torso_angle,
            "shoulder_tilt": shoulder_tilt,

            "torso_upright": (
                 UPRIGHT_MIN_ANGLE
                 <= torso_angle
                 <= UPRIGHT_MAX_ANGLE
            ),

            "torso_leaning_forward": (
                 torso_angle >= FORWARD_LEAN_MIN_ANGLE
            ),

            "shoulders_level": (
                 abs(shoulder_tilt) < SHOULDER_LEVEL_TOLERANCE
            ),
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