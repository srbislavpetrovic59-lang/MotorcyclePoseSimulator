from pose.geometry import Geometry
from pose.landmarks import PoseLandmark


class FootAnalyzer:

    def __init__(self):
        self._rear_brake_ready = False
        self._rear_brake_active = False

    def analyze(self, landmarks):
        left_knee_angle = self._left_knee_angle(landmarks)
        right_knee_angle = self._right_knee_angle(landmarks)

        left_foot_angle = self._left_foot_angle(landmarks)
        right_foot_angle = self._right_foot_angle(landmarks)
        right_ankle = landmarks[PoseLandmark.RIGHT_ANKLE]
        right_foot = landmarks[PoseLandmark.RIGHT_FOOT_INDEX]
        right_foot_rotation = self._right_foot_rotation(
            landmarks
        )
        rear_brake_ready = self._update_rear_brake_ready(
            right_foot_rotation
        )       
        print(
            "Rear brake ready:",
            rear_brake_ready,
            "rotation:",
            right_foot_rotation,
        )
        print(
            "Right foot rotation:",
            right_foot_rotation
        )
        if self._right_foot_visible(
            right_ankle,
            right_foot,
        ):
            right_foot_drop = (
                right_foot.y - right_ankle.y
            )
        else:
            right_foot_drop = None
        
        rear_brake_progress = self._rear_brake_progress(
            released_drop=0.08,
            full_drop=0.12,
            current_drop=right_foot_drop,
        )
        rear_brake_active = self._update_rear_brake_active(
            rear_brake_progress
        )
        print(
            "Rear brake:",
            f"drop={right_foot_drop}",
            f"progress={rear_brake_progress}",
            f"active={rear_brake_active}",
        )
                
        print(
            "Right foot angle:",
            right_foot_angle
        )
        return {
            "left_knee_angle": left_knee_angle,
            "right_knee_angle": right_knee_angle,
            "left_foot_angle": left_foot_angle,
            "right_foot_angle": right_foot_angle,
            "right_foot_drop": right_foot_drop,
            "left_leg_extended": left_knee_angle > 165,
            "right_leg_extended": right_knee_angle > 165,
            "rear_brake_ready": rear_brake_ready,
            "rear_brake_progress": rear_brake_progress,
            "rear_brake_active": rear_brake_active,
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
    def _right_foot_rotation(self, landmarks):
        return Geometry.angle(
            landmarks[PoseLandmark.RIGHT_HEEL],
            landmarks[PoseLandmark.RIGHT_ANKLE],
            landmarks[PoseLandmark.RIGHT_FOOT_INDEX],
        )

    @staticmethod
    def _is_rear_brake_ready(
        right_foot_rotation: float | None,
    ) -> bool:
        if right_foot_rotation is None:
            return False

        return right_foot_rotation < 90.0

    def _update_rear_brake_ready(
        self,
        right_foot_rotation: float | None,
    ) -> bool:
        if right_foot_rotation is None:
            return self._rear_brake_ready

        if right_foot_rotation < 80.0:
            self._rear_brake_ready = True
        elif right_foot_rotation > 110.0:
            self._rear_brake_ready = False

        return self._rear_brake_ready

    @staticmethod
    def _rear_brake_progress(
        released_drop: float,
        full_drop: float,
        current_drop: float | None,
    ) -> float | None:
        if current_drop is None:
            return None

        total_range = full_drop - released_drop

        if total_range == 0:
            return 0.0

        progress = (
            current_drop - released_drop
        ) / total_range

        return max(
            0.0,
            min(1.0, progress),
        )

    def _update_rear_brake_active(
        self,
        rear_brake_progress: float | None,
    ) -> bool:
        if rear_brake_progress is None:
            return self._rear_brake_active

        if self._rear_brake_active:
            if rear_brake_progress <= 0.10:
                self._rear_brake_active = False
        else:
            if rear_brake_progress >= 0.20:
                self._rear_brake_active = True

        return self._rear_brake_active

    @staticmethod
    def _right_foot_visible(
        right_ankle,
        right_foot,
    ) -> bool:
        return (
            right_ankle.visibility >= 0.5
            and right_foot.visibility >= 0.5
        )
    