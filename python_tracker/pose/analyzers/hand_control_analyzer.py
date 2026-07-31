# han#d_control_analyzer.py
from pose.landmarks import PoseLandmark
from pose.models.frame_analysis import FrameAnalysis



class HandControlAnalyzer:

    def analyze(
        self,
        frame_analysis: FrameAnalysis,
    ):
        hands = self._extract_hands(frame_analysis)

        left_hand = hands.get("Left")
        right_hand = hands.get("Right")

        left_wrist_y = (
            left_hand.landmark[0].y
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
       
        return {
            "left_hand_detected": left_hand is not None,
            "right_hand_detected": right_hand is not None,
            "left_hand_wrist_y": left_wrist_y,
            "left_wrist_to_shoulder_y": left_wrist_to_shoulder_y,
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