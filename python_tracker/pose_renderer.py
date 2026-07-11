import mediapipe as mp


class PoseRenderer:

    def __init__(self):

        self._drawing = mp.solutions.drawing_utils
        self._pose = mp.solutions.pose

    def draw(self, frame, landmarks):

        if landmarks is None:
            return frame

        self._drawing.draw_landmarks(
            frame,
            landmarks,
            self._pose.POSE_CONNECTIONS
        )

        return frame