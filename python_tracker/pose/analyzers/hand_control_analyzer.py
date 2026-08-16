# han#d_control_analyzer.py
import math
from pose.landmarks import PoseLandmark
from pose.models.frame_analysis import FrameAnalysis
from pose.geometry import Geometry
from pose.hand_landmarks import HandLandmark
from pose.models.clutch_calibration import ClutchCalibration
from pose.models.front_brake_calibration import FrontBrakeCalibration
from pose.models.throttle_calibration import ThrottleCalibration
from pathlib import Path

THROTTLE_CALIBRATION_PATH = Path(
    "config/throttle_calibration.json"
)



class HandControlAnalyzer:

    def __init__(self):
        self.clutch_calibration = ClutchCalibration()
        self._front_brake_calibration = FrontBrakeCalibration()
        self._front_brake_active = False
        self._throttle_calibration = ThrottleCalibration.load(
            THROTTLE_CALIBRATION_PATH
        )
        

    def analyze(
        self,
        frame_analysis: FrameAnalysis,
        left_index_finger_bend: float | None = None,
        right_index_finger_bend: float | None = None,
    ):
        hands = self._extract_hands(frame_analysis)

        left_hand = hands.get("Left")
        right_hand = hands.get("Right")
        
        left_hand_rotation = self._hand_rotation(
            left_hand,
        )
        
        right_hand_rotation = self._hand_rotation(
            right_hand
        )
        
        throttle_open = self._is_rotation_open(
            self._rotation_delta(
                neutral_rotation=260,
                current_rotation=right_hand_rotation,
                )
            )

        throttle_close = self._is_rotation_open(
            self._rotation_delta(
                neutral_rotation=180,
                current_rotation=right_hand_rotation,
                )
            )
        
        throttle_progress = self._current_throttle_progress(
            current_rotation=right_hand_rotation,
        )
        
        print(
            f"Throttle: "
            f"rotation={right_hand_rotation}, "
            f"progress={throttle_progress}"
        )    

        thumb_index_distance = None

        front_brake_progress = (
            self._current_front_brake_progress(
                current_angle=right_index_finger_bend,
            )
        )
        
        front_brake_active = self._is_front_brake_active(
            front_brake_progress,
            was_active=self._front_brake_active,
        )

        self._front_brake_active = front_brake_active
            
        clutch_progress = self._current_clutch_progress(
            current_angle=left_index_finger_bend
        )
        if left_index_finger_bend is None:
            print(
                "CLUTCH LOST: "
                f"hands={frame_analysis.hand_landmarks}"
            )
     
        clutch_in_friction_zone = (
            self._is_clutch_in_friction_zone(
                clutch_progress
            )
        )
      
              
        if left_hand is not None:
            thumb_tip = self._get_landmark(
               left_hand,
               HandLandmark.THUMB_TIP,
            )

            index_tip = self._get_landmark(
                left_hand,
                HandLandmark.INDEX_FINGER_TIP,
            )

           

            if (
                thumb_tip is not None
                and index_tip is not None
            ):
                thumb_index_distance = self._distance(
                    thumb_tip,
                    index_tip,
                )

        

        left_wrist = self._get_landmark(
            left_hand,
            HandLandmark.WRIST,
        )

        left_wrist_y = (
            left_wrist.y
            if left_wrist is not None
            else None
        )

        left_shoulder_y = (
            frame_analysis.pose_landmarks.landmark[
            PoseLandmark.LEFT_SHOULDER
            ].y
        )

        

        left_wrist_to_shoulder_y = (
            left_wrist_y - left_shoulder_y
            if left_wrist_y is not None
            else None
        )

        left_rotation_delta = self._rotation_delta(
            neutral_rotation=325.0,
            current_rotation=left_hand_rotation,
        )
 
                      
        return {
            "left_hand_detected": left_hand is not None,
            "right_hand_detected": right_hand is not None,
            "left_hand_wrist_y": left_wrist_y,
            "left_wrist_to_shoulder_y": left_wrist_to_shoulder_y,
            "thumb_index_distance": thumb_index_distance,
            "right_hand_rotation": right_hand_rotation,
            "left_hand_rotation": left_hand_rotation,
            "throttle_open": throttle_open,
            "throttle_close": throttle_close,
            "throttle_progress": throttle_progress,
            "clutch_progress": clutch_progress,
            "clutch_in_friction_zone": clutch_in_friction_zone,
            "front_brake_progress": front_brake_progress,
            "front_brake_active": front_brake_active,
        }
    
    
    def _extract_hands(
        self,
        frame_analysis: FrameAnalysis,
    ):
        if (
            frame_analysis.hand_landmarks is None
            or frame_analysis.hand_handedness is None
        ):
            return {}
        
        
        hands = {}
        
        for landmarks, handedness in zip(
            frame_analysis.hand_landmarks,
            frame_analysis.hand_handedness,
        ):
            label = handedness.classification[0].label
            hands[label] = landmarks
            
        return hands

    def _distance(
        self,
        point1,
        point2,
    ) -> float:
        return math.hypot(
            point2.x - point1.x,
            point2.y - point1.y,
        )


    def _get_landmark(
        self,
        hand,
        landmark,
    ):
        if hand is None:
            return None

        return hand.landmark[landmark]


    def _hand_rotation(
        self,
        hand,
    ) -> float | None:
        wrist = self._get_landmark(
            hand,
            HandLandmark.WRIST,
        )

        index_mcp = self._get_landmark(
            hand,
            HandLandmark.INDEX_FINGER_MCP,
        )

        pinky_mcp = self._get_landmark(
            hand,
            HandLandmark.PINKY_MCP,
        )

        if (
            wrist is None
            or index_mcp is None
            or pinky_mcp is None
        ):
            return None

        rotation = Geometry.line_angle(
            pinky_mcp,
            index_mcp,
        )
        if rotation < 0:
            rotation += 360

        return rotation

    @staticmethod
    def _rotation_delta(
        neutral_rotation: float | None,
        current_rotation: float | None,
    ) -> float | None:
        if (
            neutral_rotation is None
            or current_rotation is None
        ):
            return None

        return (
            neutral_rotation
            - current_rotation
            + 180.0
        ) % 360.0 - 180.0

    @staticmethod
    def _is_rotation_open(
        rotation_delta: float | None,
    ) -> bool:
        return (
            rotation_delta is not None
            and rotation_delta >= 20.0
        )

    @staticmethod
    def _is_rotation_close(
        rotation_delta: float | None,
    ) -> bool:
        return (
            rotation_delta is not None
            and rotation_delta < 20.0
        )

    @staticmethod
    def _is_left_rotation_active(
        rotation_delta: float | None,
    ) -> bool:
        return (
            rotation_delta is not None
            and rotation_delta >= 20.0
        )

    @staticmethod
    def _clutch_progress(
        released_angle: float,
        pulled_angle: float,
        current_angle: float,
    ) -> float:
        total_range = released_angle - pulled_angle

        if total_range == 0:
            return 0.0

        progress = (
            released_angle - current_angle
        ) / total_range

        return max(
            0.0,
            min(1.0, progress),
        )

    def _current_clutch_progress(
        self,
        current_angle: float | None,
    ) -> float | None:
        if current_angle is None:
            return None

        if not self.clutch_calibration.is_complete():
            return None

        return self._clutch_progress(
            released_angle=self.clutch_calibration.released_angle,
            pulled_angle=self.clutch_calibration.pulled_angle,
            current_angle=current_angle,
        )

    def calibrate_clutch_released(
        self,
        current_angle: float,
    ) -> None:
        self.clutch_calibration.set_released(
            current_angle
        )

    def calibrate_clutch_pulled(
        self,
        current_angle: float,
    ) -> None:
        self.clutch_calibration.set_pulled(
            current_angle
        )

    @staticmethod
    def _is_clutch_in_friction_zone(
        clutch_progress: float | None,
    ) -> bool:
        if clutch_progress is None:
            return False

        return 0.55 <= clutch_progress <= 0.70

    @staticmethod
    def _front_brake_progress(
        released_angle: float,
        pulled_angle: float,
        current_angle: float,
    ) -> float:
        total_range = released_angle - pulled_angle

        if total_range == 0:
            return 0.0

        progress = (
            released_angle - current_angle
        ) / total_range

        return max(
            0.0,
            min(1.0, progress),
        )

    def _current_front_brake_progress(
        self,
        current_angle: float | None,
    ) -> float | None:
        if (
            current_angle is None
            or not self._front_brake_calibration.is_complete()
        ):
            return None

        return self._front_brake_progress(
            released_angle=self._front_brake_calibration.released_angle,
            pulled_angle=self._front_brake_calibration.pulled_angle,
            current_angle=current_angle,
        )

    def calibrate_front_brake_released(
        self,
        angle: float,
    ) -> None:
        self._front_brake_calibration.set_released(angle)

    def calibrate_front_brake_pulled(
        self,
        angle: float,
    ) -> None:
        self._front_brake_calibration.set_pulled(angle)

    def capture_front_brake_released(
        self,
        current_angle: float,
    ) -> None:
        self.calibrate_front_brake_released(
            current_angle
        )

    def capture_front_brake_pulled(
        self,
        current_angle: float,
    ) -> None:
        self.calibrate_front_brake_pulled(
            current_angle
        )

    @staticmethod
    def _is_front_brake_active(
        front_brake_progress: float | None,
        was_active: bool = False,
    ) -> bool:
        if front_brake_progress is None:
            return False

        if was_active:
            return front_brake_progress > 0.06

        return front_brake_progress >= 0.12

    @staticmethod
    def _throttle_progress(
        closed_rotation: float,
        open_rotation: float,
        current_rotation: float,
    ) -> float:
        def signed_delta(
            start: float,
            end: float,
        ) -> float:
            delta = (
                (end - start + 180.0)
                % 360.0
            ) - 180.0

            # Tačno 180° je dvosmisleno.
            # Za naš throttle tretiramo ga kao pozitivan smer.
            if delta == -180.0:
                delta = 180.0

            return delta

        total_range = signed_delta(
            closed_rotation,
            open_rotation,
        )

        if total_range == 0:
            return 0.0

        current_range = signed_delta(
            closed_rotation,
            current_rotation,
        )

        progress = current_range / total_range

        return max(
            0.0,
            min(1.0, progress),
        )

    def _current_throttle_progress(
        self,
        current_rotation: float | None,
    ) -> float | None:
        if current_rotation is None:
            return None

        if not self._throttle_calibration.is_complete():
            return None

        return self._throttle_progress(
            closed_rotation=self._throttle_calibration.closed_rotation,
            open_rotation=self._throttle_calibration.open_rotation,
            current_rotation=current_rotation,
        )
    def calibrate_throttle_closed(
        self,
        current_rotation: float,
    ) -> None:
        self._throttle_calibration.set_closed(
            current_rotation
        )
        self._throttle_calibration.save(
        THROTTLE_CALIBRATION_PATH
        )

    def calibrate_throttle_open(
        self,
        current_rotation: float,
    ) -> None:
        self._throttle_calibration.set_open(
            current_rotation
        )
        self._throttle_calibration.save(
        THROTTLE_CALIBRATION_PATH
        )

    def capture_throttle_closed(
        self,
        current_rotation: float,
    ) -> None:
        self.calibrate_throttle_closed(
            current_rotation
        )
    def capture_throttle_open(
        self,
        current_rotation: float,
    ) -> None:
        self.calibrate_throttle_open(
            current_rotation
        )