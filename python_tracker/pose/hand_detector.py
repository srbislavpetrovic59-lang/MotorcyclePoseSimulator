import cv2
import mediapipe as mp


class HandDetector:

    def __init__(self):
        self._mp_hands = mp.solutions.hands
        self._hands = self._mp_hands.Hands( 
        static_image_mode=False,
        max_num_hands=2,
        model_complexity=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )
        pass

    def process(self, frame):
        return None

    def close(self):
        pass