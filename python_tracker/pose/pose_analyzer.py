# pose_analyzer.py

import mediapipe as mp

from pose.analyzers.arm_analyzer import ArmAnalyzer


class PoseAnalyzer:

    def __init__(self):
        self.arm_analyzer = ArmAnalyzer()

    def analyze(self, landmarks):
        landmark_list = (
            landmarks.landmark
            if hasattr(landmarks, "landmark")
            else landmarks
        )

        result = {}

        arm_result = self.arm_analyzer.analyze(landmark_list)
        result.update(arm_result)

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