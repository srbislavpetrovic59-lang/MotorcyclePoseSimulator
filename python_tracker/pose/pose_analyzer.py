# pose_analyzer.py

import mediapipe as mp

from pose.analyzers.arm_analyzer import ArmAnalyzer
from pose.analyzers.body_analyzer import BodyAnalyzer
from pose.analyzers.foot_analyzer import FootAnalyzer
from pose.analyzers.head_analyzer import HeadAnalyzer
from pose.analyzers.hand_control_analyzer import HandControlAnalyzer
from pose.models.frame_analysis import FrameAnalysis
from pose.analyzers.hand_analyzer import HandAnalyzer



class PoseAnalyzer:

    def __init__(self):
        self.arm_analyzer = ArmAnalyzer()
        self.body_analyzer = BodyAnalyzer()
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


    def analyze(self, frame_analysis: FrameAnalysis):
        landmarks = frame_analysis.pose_landmarks

        landmark_list = (
            landmarks.landmark
            if hasattr(landmarks, "landmark")
            else landmarks
        )

        result = {}
        
        throttle_open = False
        throttle_close = False
        
        arm_result = self.arm_analyzer.analyze(landmark_list)
        result.update(arm_result)

        body_result = self.body_analyzer.analyze(landmark_list)
        result.update(body_result)

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

        throttle_open = hand_control_result["throttle_open"]
        result.update(hand_control_result)

        throttle_close = hand_control_result["throttle_close"]
        result.update(hand_control_result)
       
        
        result["pose_confidence"] = self._calculate_pose_confidence(
            landmark_list
        )

        

        result["rider_state"] = self._determine_rider_state(result)
       
        
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

    