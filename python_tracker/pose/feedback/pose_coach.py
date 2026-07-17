import time

from pose.models.feedback_item import FeedbackItem


class PoseCoach:

    def __init__(
        self,
        cooldown_seconds: float = 3.0,
        activation_delay: float = 1.5,
    ) -> None:
        self.cooldown_seconds = cooldown_seconds
        self.activation_delay = activation_delay

        self._current_message: str | None = None
        self._current_message_since = 0.0

        self._last_spoken_by_message: dict[str, float] = {}

    def update(
        self,
        feedback: FeedbackItem | None,
    ) -> None:
        if feedback is None:
            self._reset()
            return

        now = time.monotonic()

        # Wait until the same posture issue persists long enough.
        if self._detect_feedback_change(feedback, now):
            return

        if not self._is_activation_delay_elapsed(now):
            return

        if self._is_on_cooldown(feedback, now):
            return

        self._speak(feedback, now)

    def _reset(self) -> None:
        self._current_message = None
        self._current_message_since = 0.0

    def _detect_feedback_change(
        self,
        feedback: FeedbackItem,
        now: float,
    ) -> bool:
        if feedback.message == self._current_message:
            return False

        self._current_message = feedback.message
        self._current_message_since = now

        return True

    def _is_activation_delay_elapsed(
        self,
        now: float,
    ) -> bool:
        elapsed = now - self._current_message_since
        return elapsed >= self.activation_delay

    def _is_on_cooldown(
        self,
        feedback: FeedbackItem,
        now: float,
    ) -> bool:
        last_spoken = self._last_spoken_by_message.get(
            feedback.message,
            0.0,
        )

        return now - last_spoken < self.cooldown_seconds

    def _speak(
        self,
        feedback: FeedbackItem,
        now: float,
    ) -> None:
        print(f"[Coach] {feedback.message}")

        self._last_spoken_by_message[feedback.message] = now