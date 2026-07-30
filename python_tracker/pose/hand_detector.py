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

    def detect(self, frame):
        """
        Detects hands and returns MediaPipe hand landmarks.

        Returns:
            list | None
        """
        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        results = self._hands.process(rgb_frame)

        return results.multi_hand_landmarks

    def close(self):
        self._hands.close()
       