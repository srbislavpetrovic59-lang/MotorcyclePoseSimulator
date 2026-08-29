import time
from pose.geometry import Geometry
from pose.landmarks import PoseLandmark
from pose.analyzers.gear_shift_detector import GearShiftDetector


class FootAnalyzer:

    def __init__(self):
        self._rear_brake_ready = False
        self._rear_brake_active = False
        self._right_foot_was_visible = False
        self._right_foot_seen_once = False
        self._start_time = time.monotonic() 
        self._gear_shift_detector = GearShiftDetector()

    def analyze(self, landmarks):
        left_knee_angle = self._left_knee_angle(landmarks)
        right_knee_angle = self._right_knee_angle(landmarks)

        left_foot_angle = self._left_foot_angle(landmarks)
        right_foot_angle = self._right_foot_angle(landmarks)
        
        left_heel = landmarks[PoseLandmark.LEFT_HEEL]
        left_ankle = landmarks[PoseLandmark.LEFT_ANKLE]
        left_foot = landmarks[PoseLandmark.LEFT_FOOT_INDEX]

        left_foot_is_visible = self._left_foot_visible(
            left_heel,
            left_ankle,
            left_foot,
        )

        elapsed = time.monotonic() - self._start_time
        gear_shift = None
        if left_foot_is_visible:
            left_foot_drop = (
                left_foot.y - left_ankle.y
            )
            
            left_foot_forward = (
                left_foot.x - left_ankle.x
            )
            
            gear_shift = self._gear_shift_detector.update(
                left_foot_drop,
                left_foot_angle,
                left_foot_forward=left_foot_forward,
                elapsed_seconds=elapsed,
            )

            if gear_shift is not None:
                print(
                    "GEAR SHIFT:",
                    gear_shift,
                )
        else:
            left_foot_drop = None
        
        
        left_foot_forward = left_foot.x - left_ankle.x  #testnapred nazad
        print(
            "LEFT FOOT FORWARD:",
            f"t={elapsed:.3f}",
            f"value={left_foot_forward:.4f}",
        )
        print(
            "Left foot:",
            f"t={elapsed:.3f}, "
            f"drop={left_foot_drop}",
            f"angle={left_foot_angle:.1f}",
        )
       
        print(
            "LEFT FOOT XYZ:",
            f"t={elapsed:.3f}",
            f"heel=({left_heel.x:.3f}, {left_heel.y:.3f}, {left_heel.z:.3f})",
            f"ankle=({left_ankle.x:.3f}, {left_ankle.y:.3f}, {left_ankle.z:.3f})",
            f"toe=({left_foot.x:.3f}, {left_foot.y:.3f}, {left_foot.z:.3f})",
        )
        print(
            "Left visibility:",
            f"heel={left_heel.visibility:.2f}",
            f"ankle={left_ankle.visibility:.2f}",
            f"foot={left_foot.visibility:.2f}",
        )

        right_heel = landmarks[PoseLandmark.RIGHT_HEEL]
        right_ankle = landmarks[PoseLandmark.RIGHT_ANKLE]
        right_foot = landmarks[PoseLandmark.RIGHT_FOOT_INDEX]

        right_foot_is_visible = self._right_foot_visible(
            right_heel,
            right_ankle,
            right_foot,
        )
        right_foot_reacquired = (
            right_foot_is_visible
            and self._right_foot_seen_once
            and not self._right_foot_was_visible
        )

        if right_foot_is_visible:
            right_foot_rotation = self._right_foot_rotation(
                landmarks
            )

            if right_foot_reacquired:
                rear_brake_ready = None
            else:
                rear_brake_ready = self._update_rear_brake_ready(
                    right_foot_rotation
                )

            right_foot_drop = (
                right_foot.y - right_ankle.y
            )
        else:
            right_foot_rotation = None
            right_foot_drop = None
            rear_brake_ready = None
        '''
        print(
            "Rear brake ready:",
            rear_brake_ready,
            "rotation:",
            right_foot_rotation,
        )

        print(
            "Right foot rotation:",
            right_foot_rotation
        )'''
        if right_foot_reacquired:
            rear_brake_progress = None
        else:
            rear_brake_progress = self._rear_brake_progress(
                released_drop=0.08,
                full_drop=0.12,
                current_drop=right_foot_drop,
            )

        rear_brake_active = self._update_rear_brake_active(
            rear_brake_progress
        )

        '''
        print(
            "Rear brake:",
            f"drop={right_foot_drop}",
            f"progress={rear_brake_progress}",
            f"active={rear_brake_active}",
        )
                
        print(
            "Right foot angle:",
            right_foot_angle
        )'''
        if right_foot_is_visible:
            self._right_foot_seen_once = True

        self._right_foot_was_visible = right_foot_is_visible

        return {
            "left_knee_angle": left_knee_angle,
            "right_knee_angle": right_knee_angle,
            "left_foot_angle": left_foot_angle,
            "right_foot_angle": right_foot_angle,
            "left_foot_drop": left_foot_drop,
            "right_foot_drop": right_foot_drop,
            "left_leg_extended": left_knee_angle > 165,
            "right_leg_extended": right_knee_angle > 165,
            "rear_brake_ready": rear_brake_ready,
            "rear_brake_progress": rear_brake_progress,
            "rear_brake_active": rear_brake_active,
            "gear_shift": gear_shift,
            "leg_symmetry": round(
                max(0.0, 100.0 - abs(left_knee_angle - right_knee_angle)),
                1,
            ),
            "elapsed_time": elapsed,
            
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
        right_heel,
        right_ankle,
        right_foot,
    ) -> bool:
        return (
            right_heel.visibility >= 0.5
            and right_ankle.visibility >= 0.5
            and right_foot.visibility >= 0.5
        )

    @staticmethod
    def _left_foot_visible(
        left_heel,
        left_ankle,
        left_foot,
    ) -> bool:
        return (
            left_heel.visibility >= 0.5
            and left_ankle.visibility >= 0.5
            and left_foot.visibility >= 0.5
        )
    