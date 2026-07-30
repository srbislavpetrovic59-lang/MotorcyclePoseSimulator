# pose_detector.py

import cv2
import mediapipe as mp


class PoseDetector:

    def __init__(self):

        self._mp_pose = mp.solutions.pose
        self._pose = self._mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def detect(self, frame):

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        results = self._pose.process(rgb_frame)

        return results.pose_landmarks

    def release(self):
        self._pose.close()

