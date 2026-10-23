# pose_analyzer.py
import time
import math

import mediapipe as mp

from pose.analyzers.arm_analyzer import ArmAnalyzer
from pose.analyzers.body_analyzer import BodyAnalyzer
from pose.analyzers.foot_analyzer import FootAnalyzer
from pose.analyzers.head_analyzer import HeadAnalyzer
from pose.analyzers.hand_control_analyzer import HandControlAnalyzer
from pose.models.frame_analysis import FrameAnalysis
from pose.analyzers.hand_analyzer import HandAnalyzer
from pose.analyzers.riding_phase_detector import RidingPhaseDetector
from pose.analyzers.lean_detector import LeanDetector
from pose.analyzers.handlebar_steering_detector import HandlebarSteeringDetector



class PoseAnalyzer:

    def __init__(self):
        self.arm_analyzer = ArmAnalyzer()
        self.body_analyzer = BodyAnalyzer()
        self.lean_detector = LeanDetector()
        self._handlebar_steering_detector = HandlebarSteeringDetector()
        self._handlebar_calibration_samples = []
        self._lean_calibration_requested = False
        self._lean_calibration_requested_at = None
        self.foot_analyzer = FootAnalyzer()
        self._head_analyzer = HeadAnalyzer()
        self._hand_control_analyzer = HandControlAnalyzer()
        self._hand_control_analyzer.calibrate_front_brake_released(
            150.0
        )

        self._hand_control_analyzer.calibrate_front_brake_pulled(
            106.0
        )
        self._hand_analyzer = HandAnalyzer()
        self._hand_control_analyzer.calibrate_clutch_released(
            176.0
        )
        self._hand_control_analyzer.calibrate_clutch_pulled(
            131.0
        )
        self._riding_phase_detector = RidingPhaseDetector()

    
    def calibrate_front_brake_released(
        self,
        current_angle: float,
    ) -> None:
        self._hand_control_analyzer.calibrate_front_brake_released(
            current_angle
        )

    def calibrate_front_brake_pulled(
        self,
        current_angle: float,
    ) -> None:
        self._hand_control_analyzer.calibrate_front_brake_pulled(
            current_angle
        )

    def calibrate_clutch_released(
        self,
        current_angle: float,
    ) -> None:
        self._hand_control_analyzer.calibrate_clutch_released(
            current_angle
        )

    def calibrate_clutch_pulled(
        self,
        current_angle: float,
    ) -> None:
        self._hand_control_analyzer.calibrate_clutch_pulled(
            current_angle
        )

    def analyze(self, frame_analysis: FrameAnalysis):
        landmarks = frame_analysis.pose_landmarks

        landmark_list = (
            landmarks.landmark
            if hasattr(landmarks, "landmark")
            else landmarks
        )

        result = {}
        
             
        arm_result = self.arm_analyzer.analyze(landmark_list)
        result.update(arm_result)

        body_result = self.body_analyzer.analyze(landmark_list)

        body_result = self._add_lean_to_result(body_result)

        result.update(body_result)

        print(
            f"Shoulder tilt: {body_result['shoulder_tilt']:+7.2f} deg | "
            f"Lean: {body_result['lean_normalized']:+.3f} ",
            end="\r",
            flush=True,
        )        

        foot_result = self.foot_analyzer.analyze(landmark_list)
        result.update(foot_result)
        
        head_result = self._head_analyzer.analyze(landmark_list)
        result.update(head_result)
        
        hands = self._hand_control_analyzer._extract_hands(
            frame_analysis
        )

        hand_result = self._hand_analyzer.analyze(
            hands
        )
        result.update(hand_result)
       
        hand_control_result = self._hand_control_analyzer.analyze(
            frame_analysis,
            left_index_finger_bend=hand_result[
                "left_index_finger_bend"
            ],
            right_index_finger_bend=hand_result[
                "right_index_finger_bend"
            ],
        )
        result.update(hand_control_result)

        
        result["pose_confidence"] = self._calculate_pose_confidence(
            landmark_list
        )

        left_wrist = landmark_list[
            mp.solutions.pose.PoseLandmark.LEFT_WRIST
        ]

        right_wrist = landmark_list[
            mp.solutions.pose.PoseLandmark.RIGHT_WRIST
        ]


        left_shoulder = landmark_list[
            mp.solutions.pose.PoseLandmark.LEFT_SHOULDER
        ]
        right_shoulder = landmark_list[
            mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER
        ]

        left_x = left_wrist.x - left_shoulder.x
        right_x = right_wrist.x - right_shoulder.x

        left_z = left_wrist.z - left_shoulder.z
        right_z = right_wrist.z - right_shoulder.z

        if self._handlebar_steering_detector._neutral_x_difference is None:
           self._handlebar_calibration_samples.append(
                (left_x, right_x, left_z, right_z)
            )

           if len(self._handlebar_calibration_samples) >= 30:
               self._handlebar_steering_detector.calibrate_x_samples(
                   self._handlebar_calibration_samples
               )

        handlebar_steering = self._handlebar_steering_detector.update_x(
            left_wrist_x=left_x,
            right_wrist_x=right_x,
        )

        result["handlebar_steering"] = handlebar_steering
           
       
        print(
            f"Handlebar steering: {handlebar_steering:+.3f}",
            end="\r",
            flush=True,
        )

        print(
            f"LX: {left_x:+.3f} | "
            f"RX: {right_x:+.3f} | "
            f"XDiff: {left_x - right_x:+.3f} | "
            f"ZDiff: {left_wrist.z - right_wrist.z:+.3f}",
            end="\r",
            flush=True,
        )

        print(
            f"Steering hands: "
            f"LX={left_x:+.3f} | "
            f"RX={right_x:+.3f}"
        )


        riding_phase = self._riding_phase_detector.update(
            throttle_progress=result["throttle_progress"],
            front_brake_progress=result["front_brake_progress"],
            rear_brake_progress=result["rear_brake_progress"],
            torso_angle=result["torso_angle"],
        )


        result["riding_phase"] = riding_phase.value
        

        result["rider_state"] = self._determine_rider_state(result)
       
        
        return result

    def _calculate_lean(self, shoulder_tilt: float) -> float:
        return self.lean_detector.update_normalized(
            shoulder_tilt
        )

    def calibrate_lean(self, shoulder_tilt: float) -> None:
        self.lean_detector.calibrate(shoulder_tilt)
    
    def request_lean_calibration(self, now=None) -> None:
        if now is None:
            now = time.monotonic()

        self._lean_calibration_requested = True
        self._lean_calibration_requested_at = now

    def _add_lean_to_result(
        self,
        body_result: dict,
        now=None,
    ) -> dict:
        if now is None:
            now = time.monotonic()

        result = body_result.copy()
        shoulder_tilt = body_result["shoulder_tilt"]

        # Podrazumevano nema događaja završetka.
        result["lean_calibration_completed"] = False

        if self._lean_calibration_requested:
            elapsed = now - self._lean_calibration_requested_at

            if elapsed >= 3.0:
                self.calibrate_lean(shoulder_tilt)

                self._lean_calibration_requested = False
                self._lean_calibration_requested_at = None

                # Događaj se pojavljuje samo u ovom frejmu.
                result["lean_calibration_completed"] = True

        result["lean_normalized"] = self._calculate_lean(
            shoulder_tilt
        )

        return result


    @staticmethod
    def _calculate_pose_confidence(landmarks) -> float:
        required_indices = [
            mp.solutions.pose.PoseLandmark.LEFT_SHOULDER,
            mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER,
            mp.solutions.pose.PoseLandmark.LEFT_ELBOW,
            mp.solutions.pose.PoseLandmark.RIGHT_ELBOW,
            mp.solutions.pose.PoseLandmark.LEFT_WRIST,
            mp.solutions.pose.PoseLandmark.RIGHT_WRIST,
        ]

        visibility_values = [
            landmarks[index].visibility
            for index in required_indices
        ]

        confidence = sum(visibility_values) / len(visibility_values)
        return round(confidence, 3)

    @staticmethod
    def _determine_rider_state(result):
        return "UNKNOWN"

    def capture_throttle_closed(
        self,
        current_rotation: float,
    ) -> None:
        self._hand_control_analyzer.capture_throttle_closed(
            current_rotation
        )


    def capture_throttle_open(
        self,
        current_rotation: float,
    ) -> None:
        self._hand_control_analyzer.capture_throttle_open(
            current_rotation
        )

    