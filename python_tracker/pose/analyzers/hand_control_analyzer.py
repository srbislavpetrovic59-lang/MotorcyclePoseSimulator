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
        right_hand = hands.get("Right")

        thumb_index_distance = None

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


    def _get_landmark(
        self,
        hand,
        landmark,
    ):
        if hand is None:
            return None

        return hand.landmark[landmark]