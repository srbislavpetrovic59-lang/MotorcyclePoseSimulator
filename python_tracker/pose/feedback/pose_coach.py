import time

from pose.models.feedback_item import FeedbackItem


class PoseCoach:

    def __init__(self, cooldown_seconds: float = 3.0):
        self.cooldown_seconds = cooldown_seconds
        self._last_feedback_message: str | None = None
        self._last_feedback_time = 0.0
        self.activation_delay = 1.5

        self._current_message: str | None = None
        self._current_message_since = 0.0
        self._last_spoken_by_message: dict[str, float] = {}


    def update(self, feedback: FeedbackItem | None) -> None:
        if feedback is None:
            self._current_message = None
            self._current_message_since = 0.0
            return

        now = time.monotonic()

        if feedback.message != self._current_message:
            self._current_message = feedback.message
            self._current_message_since = now
            return

        if now - self._current_message_since < self.activation_delay:
            return

        last_spoken = self._last_spoken_by_message.get(
            feedback.message,
            0.0,
        )

        if now - last_spoken < self.cooldown_seconds:
            return

        print(f"[Coach] {feedback.message}")

        self._last_spoken_by_message[feedback.message] = now