import time
from pose.geometry import Geometry
from pose.landmarks import PoseLandmark
from pose.analyzers.gear_shift_detector import GearShiftDetector
from statistics import median


class FootAnalyzer:

    def __init__(self):
        self._rear_brake_ready = False
        self._rear_brake_active = False
        self._right_foot_was_visible = False
        self._right_foot_seen_once = False
        self._right_foot_forward_baseline = None
        self._right_foot_forward_baseline_samples = []
        self._right_ankle_depth_baseline = None
        self._right_ankle_depth_baseline_samples = []
        self._rear_brake_prepare = False
        self._right_foot_angle_baseline = None
        self._right_foot_angle_baseline_samples = []
        self._right_foot_released_drop_baseline = None
        self._right_foot_released_drop_baseline_samples = []
        self._start_time = time.monotonic() 
        self._gear_shift_detector = GearShiftDetector()
        self._left_foot_gear_was_visible = 0
        self._left_foot_gear_visibility_grace = 0
        self._rear_brake_active_frames = 0
        self._depth_displacement_samples = []
        self._rear_brake_not_ready_frames = 0
        
        

    def analyze(self, landmarks):
        left_knee_angle = self._left_knee_angle(landmarks)
        right_knee_angle = self._right_knee_angle(landmarks)

        left_foot_angle = self._left_foot_angle(landmarks)
        right_foot_angle = self._right_foot_angle(landmarks)
        
        left_heel = landmarks[PoseLandmark.LEFT_HEEL]
        left_ankle = landmarks[PoseLandmark.LEFT_ANKLE]
        left_foot = landmarks[PoseLandmark.LEFT_FOOT_INDEX]
        left_heel_relative_y = left_heel.y - left_foot.y

        left_foot_is_visible = self._left_foot_visible_for_gear_shift(
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
                left_heel_y=left_heel.y,
                left_heel_visibility=left_heel.visibility,
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
            f"LEFT HEEL REL Y: "
            f"t={elapsed:.3f} "
            f"value={left_heel_relative_y:.4f}"
        )
        print(
            f"LEFT HEEL Y: "
            f"t={elapsed:.3f} "
            f"value={left_heel.y:.4f}"
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

        # Privremena kalibracija za kontrolisani test.
        if 5.0 <= elapsed < 10.0 and right_foot_is_visible:
            self._update_right_ankle_depth_baseline(
                right_ankle.z
            )
        # Kraj privremene kalibracije.

        filtered_displacement = None

        if right_foot_is_visible:
            baseline = self._right_ankle_depth_baseline

            displacement = (
                self._right_ankle_depth_displacement(
                    right_ankle.z,
                    baseline,
                )
                if baseline is not None
                else None
            )

            filtered_displacement = (
                self._filter_depth_displacement(displacement)
                if displacement is not None
                else None
            )

            print(
                "RIGHT ANKLE DEPTH:",
                f"t={elapsed:.3f}",
                f"z={right_ankle.z:.4f}",
                f"baseline={baseline}",
                f"displacement={displacement}",
                f"filtered={filtered_displacement}",
            )
        right_foot_reacquired = (
            right_foot_is_visible
            and self._right_foot_seen_once
            and not self._right_foot_was_visible
        )

        if right_foot_is_visible:
            #================ samo za test
            print(
                "RIGHT FOOT XYZ:",
                f"t={elapsed:.3f}",
                f"heel=({right_heel.x:.4f}, {right_heel.y:.4f}, {right_heel.z:.4f})",
                f"ankle=({right_ankle.x:.4f}, {right_ankle.y:.4f}, {right_ankle.z:.4f})",
                f"toe=({right_foot.x:.4f}, {right_foot.y:.4f}, {right_foot.z:.4f})",
            )
            #+++++++++++++++ kraj testa           
            
            right_foot_rotation = self._right_foot_rotation(
                landmarks
            )

            if right_foot_reacquired:
                rear_brake_ready = None
            else:
                rear_brake_ready = self._update_rear_brake_ready(
                    right_foot_rotation,
                    filtered_displacement,
                )

            self._reset_rear_brake_prepare_if_not_ready(
                rear_brake_ready
            )
            
            right_foot_drop = (
                right_foot.y - right_ankle.y
            )

            self._update_rear_brake_released_drop_baseline(
                right_foot_drop=right_foot_drop,
                elapsed_seconds=elapsed,
            )

            right_foot_forward = (
                right_foot.x - right_ankle.x
            )

            self._update_rear_brake_angle_baseline(
                right_foot_angle
            )

            if (
                self._right_foot_angle_baseline is not None
                and self._right_foot_released_drop_baseline is not None
            ):
                self._update_rear_brake_motion(
                    right_foot_angle=right_foot_angle,
                    baseline_angle=self._right_foot_angle_baseline,
                    right_foot_drop=right_foot_drop,
                    released_drop=self._right_foot_released_drop_baseline,
                )

            self._update_rear_brake_forward_baseline_if_released(
                right_foot_forward=right_foot_forward,
                rear_brake_ready=rear_brake_ready,
            )


            print(
                "RIGHT BRAKE MOTION:",
                f"forward={right_foot_forward:.4f}",
                f"baseline={self._right_foot_forward_baseline}",
                f"drop={right_foot_drop:.4f}",
                f"ready={rear_brake_ready}",
                f"angle={right_foot_angle:.1f}",
                f"prepare={self._rear_brake_prepare}",
                f"active={self._rear_brake_active}",
                f"released_drop={self._right_foot_released_drop_baseline}",
                f"rotation={right_foot_rotation} ",
                f"RIGHT FOOT POSITION: "
                f"t={elapsed:.3f} "
                f"ankle_y={right_ankle.y:.4f} "
                f"toe_y={right_foot.y:.4f}"

            )
        
        else:
            right_foot_rotation = None
            right_foot_drop = None
            rear_brake_ready = None
            right_foot_forward = None
        
        if right_foot_reacquired or not right_foot_is_visible:
            rear_brake_progress = None
        else:
            rear_brake_progress = self._rear_brake_progress_from_motion(
                right_foot_forward=right_foot_forward,
                right_foot_drop=right_foot_drop,
                forward_baseline=self._right_foot_forward_baseline,
                released_drop=0.08,
                full_drop=0.12,
            )
            print(
                "REAR BRAKE MOTION PROGRESS:",
                rear_brake_progress,
            )

        rear_brake_active = self._update_rear_brake_active(
            rear_brake_progress
        )

       
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
        filtered_depth_displacement: float | None = None,
    ) -> bool:
        if right_foot_rotation is None:
            self._rear_brake_not_ready_frames = 0
            return self._rear_brake_ready

        if right_foot_rotation < 80.0:
            depth_confirmed = (
                filtered_depth_displacement is None
                or (
                    filtered_depth_displacement is not None
                    and filtered_depth_displacement < -0.025
                )
            )

            if depth_confirmed:
                self._rear_brake_ready = True

            self._rear_brake_not_ready_frames = 0

        elif right_foot_rotation > 110.0:
            self._rear_brake_not_ready_frames += 1

            if self._rear_brake_not_ready_frames >= 2:
                self._rear_brake_ready = False

        else:
            self._rear_brake_not_ready_frames = 0

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
                self._rear_brake_active_frames += 1

                if self._rear_brake_active_frames >= 2:
                    self._rear_brake_active = False
                    self._rear_brake_active_frames = 0
            else:
                self._rear_brake_active_frames = 0
        else:
            self._rear_brake_active_frames = 0

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

    def _left_foot_visible_for_gear_shift(
        self,
        left_heel,
        left_ankle,
        left_foot,
    ) -> bool:
        normally_visible = (
            left_heel.visibility >= 0.5
            and left_ankle.visibility >= 0.30
            and left_foot.visibility >= 0.45
        )

        if normally_visible:
            self._left_foot_gear_visibility_grace = 2
            return True

        briefly_degraded = (
            self._left_foot_gear_visibility_grace > 0
            and left_heel.visibility >= 0.5
            and left_ankle.visibility >= 0.30
            and left_foot.visibility >= 0.45
        )

        if briefly_degraded:
            self._left_foot_gear_visibility_grace -= 1
            return True

        self._left_foot_gear_visibility_grace = 0
        return False


    def _rear_brake_progress_from_motion(
        self,
        right_foot_forward,
        right_foot_drop,
        forward_baseline,
        released_drop,
        full_drop,
    ):
       forward_threshold = 0.0025
       if forward_baseline is None:
           return 0.0


       if right_foot_forward - forward_baseline < forward_threshold:
            return 0.0

       drop_range = full_drop - released_drop

       if drop_range <= 0.0:
           return 0.0

       progress = (right_foot_drop - released_drop) / drop_range

       return max(0.0, min(1.0, progress))


    def _update_rear_brake_forward_baseline(
        self,
        right_foot_forward,
    ):
        if self._right_foot_forward_baseline is None:
            self._right_foot_forward_baseline_samples.append(
                right_foot_forward
            )

            if len(self._right_foot_forward_baseline_samples) >= 5:
                samples = self._right_foot_forward_baseline_samples[-5:]

                if max(samples) - min(samples) <= 0.01:
                    self._right_foot_forward_baseline = (
                        sum(samples) / 5
                    )

    def _update_rear_brake_forward_baseline_if_released(
        self,
        right_foot_forward,
        rear_brake_ready,
    ):
       
        self._update_rear_brake_forward_baseline(
            right_foot_forward
            )

    @staticmethod
    def _is_rear_brake_prepare(
        current_angle: float,
        baseline_angle: float,
    ) -> bool:
        return baseline_angle - current_angle >= 4.0

    def _update_rear_brake_prepare(
        self,
        current_angle: float,
        baseline_angle: float,
    ) -> bool:
        if self._is_rear_brake_prepare(
            current_angle,
            baseline_angle,
        ):
            self._rear_brake_prepare = True

        return self._rear_brake_prepare

    def _is_rear_brake_press(
        self,
        right_foot_drop: float,
        released_drop: float,
    ) -> bool:
        if not self._rear_brake_prepare:
            return False

        return right_foot_drop - released_drop >= 0.02


    def _update_rear_brake_active_from_press(
        self,
        pressing: bool,
    ) -> bool:
        if pressing:
            self._rear_brake_active = True

        return self._rear_brake_active

    def _update_rear_brake_motion(
        self,
        right_foot_angle: float,
        baseline_angle: float,
        right_foot_drop: float,
        released_drop: float,
    ) -> bool:
        if not self._rear_brake_ready:
            self._rear_brake_prepare = False
            return False
        self._update_rear_brake_prepare(
            current_angle=right_foot_angle,
            baseline_angle=baseline_angle,
        )

        pressing = self._is_rear_brake_press(
            right_foot_drop=right_foot_drop,
            released_drop=released_drop,
        )

        return self._update_rear_brake_active_from_press(
            pressing
        )

    def _update_rear_brake_angle_baseline(
        self,
        right_foot_angle: float,
    ):
        if self._right_foot_angle_baseline is None:
            self._right_foot_angle_baseline_samples.append(
                right_foot_angle
            )

            if len(self._right_foot_angle_baseline_samples) >= 5:
                samples = self._right_foot_angle_baseline_samples[-5:]
                if max(samples) - min(samples) <= 1.0:
                    self._right_foot_angle_baseline = (
                        sum(samples) / 5
                    )

    def _reset_rear_brake_prepare_if_not_ready(
        self,
        rear_brake_ready: bool | None,
    ):
        if rear_brake_ready is False:
            self._rear_brake_prepare = False
            self._rear_brake_active = False

    def _update_rear_brake_released_drop_baseline(
        self,
        right_foot_drop: float,
        elapsed_seconds=None,
    ):
        if (
            elapsed_seconds is not None
            and elapsed_seconds < 5.0
        ):
            return

        if self._right_foot_released_drop_baseline is None:
            self._right_foot_released_drop_baseline_samples.append(
                right_foot_drop
            )

            if len(self._right_foot_released_drop_baseline_samples) >= 5:
                samples = (
                    self._right_foot_released_drop_baseline_samples[-5:]
                )

                if max(samples) - min(samples) <= 0.01:
                    self._right_foot_released_drop_baseline = (
                        sum(samples) / 5
                    )


    @staticmethod
    def _right_ankle_depth_displacement(
        current_z: float,
        baseline_z: float,
    ) -> float:
        return current_z - baseline_z

    def _update_right_ankle_depth_baseline(
        self,
        right_ankle_z: float,
    ) -> None:
        if self._right_ankle_depth_baseline is None:
            self._right_ankle_depth_baseline_samples.append(
                right_ankle_z
            )

            if len(self._right_ankle_depth_baseline_samples) >= 5:
                samples = self._right_ankle_depth_baseline_samples[-5:]

                if max(samples) - min(samples) <= 0.01:
                    self._right_ankle_depth_baseline = (
                        sum(samples) / 5
                    )

    @staticmethod
    def _depth_median(samples):
        if not samples:
            return None

        return median(samples[-5:])

    def _filter_depth_displacement(self, displacement):
        self._depth_displacement_samples.append(displacement)

        return self._depth_median(
            self._depth_displacement_samples
        )