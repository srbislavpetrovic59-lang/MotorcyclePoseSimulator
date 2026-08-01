# han#d_control_analyzer.py
import math
from pose.landmarks import PoseLandmark
from pose.models.frame_analysis import FrameAnalysis
from pose.hand_landmarks import HandLandmark



class HandControlAnalyzer:

    def analyze(
        self,
        frame_analysis: FrameAnalysis,
    ):
        hands = self._extract_hands(frame_analysis)

        left_hand = hands.get("Left")
        thumb_index_distance = None

        if left_hand is not None:
            thumb_tip = left_hand.landmark[
                HandLandmark.THUMB_TIP
            ]

            index_tip = left_hand.landmark[
                HandLandmark.INDEX_FINGER_TIP
            ]

            thumb_index_distance = self._distance(
                thumb_tip,
                index_tip,
            )

        right_hand = hands.get("Right")

        left_wrist_y = (
            left_hand.landmark[ HandLandmark.WRIST ].y
            if left_hand is not None
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
        print(
            f"Left thumb-index distance: "
            f"{thumb_index_distance}"
        )
        return {
            "left_hand_detected": left_hand is not None,
            "right_hand_detected": right_hand is not None,
            "left_hand_wrist_y": left_wrist_y,
            "left_wrist_to_shoulder_y": left_wrist_to_shoulder_y,
            "thumb_index_distance": thumb_index_distance,
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