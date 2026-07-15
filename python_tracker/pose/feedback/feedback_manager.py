import time

from .feedback_selector import FeedbackSelector
from ..models.feedback_item import FeedbackItem


class FeedbackManager:

    def __init__(self, cooldown_seconds: float = 5.0):
        self.selector = FeedbackSelector()
        self.cooldown_seconds = cooldown_seconds

        self._last_message: str | None = None
        self._last_message_time: float = 0.0

    def process(
        self,
        feedback_items: list[FeedbackItem],
    ) -> FeedbackItem | None:

        selected = self.selector.select(feedback_items)

        if selected is None:
            return None

        if not self._can_emit(selected):
            return None

        self._last_message = selected.message
        self._last_message_time = time.monotonic()

        return selected

    def _can_emit(self, item: FeedbackItem) -> bool:
        if item.message != self._last_message:
            return True

        elapsed = time.monotonic() - self._last_message_time

        return elapsed >= self.cooldown_seconds
    def display_text(
        self,
        item: FeedbackItem | None,
    ) -> str:

        if item is None:
            return "Good posture"

        return item.message

    def speak(
    self,
    item: FeedbackItem | None,
    ):

        pass
