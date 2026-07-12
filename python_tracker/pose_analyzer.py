# pose_analyzer.py
import math

import mediapipe as mp
from python_tracker.pose.analyzers.arm_analyzer import ArmAnalyzer
from rider_state import RiderState


from python_tracker.pose.analyzers.arm_analyzer import ArmAnalyzer


class PoseAnalyzer:

    def __init__(self):
        self.arm_analyzer = ArmAnalyzer()

    def analyze(self, landmarks):
        result = {}

        arm_result = self.arm_analyzer.analyze(landmarks)
        result.update(arm_result)

        return result
   
        result["rider_state"] = self._determine_rider_state(result)

        return result

        left_elbow_angle = self._calculate_joint_angle(
            landmarks.landmark[self._pose_landmark.LEFT_SHOULDER],
            landmarks.landmark[self._pose_landmark.LEFT_ELBOW],
            landmarks.landmark[self._pose_landmark.LEFT_WRIST],
        )

        right_elbow_angle = self._calculate_joint_angle(
            landmarks.landmark[self._pose_landmark.RIGHT_SHOULDER],
            landmarks.landmark[self._pose_landmark.RIGHT_ELBOW],
            landmarks.landmark[self._pose_landmark.RIGHT_WRIST],
        )

        pose_confidence = self._calculate_pose_confidence(landmarks)

        return RiderState(
            left_elbow_angle=left_elbow_angle,
            right_elbow_angle=right_elbow_angle,
            pose_confidence=pose_confidence,
        )

    @staticmethod
    def _calculate_joint_angle(point_a, point_b, point_c) -> float:
        angle_ab = math.atan2(
            point_a.y - point_b.y,
            point_a.x - point_b.x,
        )

        angle_cb = math.atan2(
            point_c.y - point_b.y,
            point_c.x - point_b.x,
        )

        angle = math.degrees(angle_cb - angle_ab)
        angle = abs(angle)

        if angle > 180.0:
            angle = 360.0 - angle

        return round(angle, 1)

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
            landmarks.landmark[index].visibility
            for index in required_indices
        ]

        confidence = sum(visibility_values) / len(visibility_values)
        return round(confidence, 3)