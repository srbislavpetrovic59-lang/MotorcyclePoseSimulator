import time

from pose.models.feedback_item import FeedbackItem


class PoseCoach:

    def __init__(self, cooldown_seconds: float = 3.0):
        self.cooldown_seconds = cooldown_seconds
        self._last_spoken_time = 0.0
        self._last_feedback_message = None

    def update(
        self,
        feedback: FeedbackItem | None,
    ):
        if feedback is None:
            return

        now = time.monotonic()

       if (
           feedback.message == self._last_feedback_message
           and now - self._last_spoken_time < self.cooldown_seconds
       ):
           return

       print(f"[Coach] {feedback.message}")

       self._last_feedback_message = feedback.message
       self._last_spoken_time = now