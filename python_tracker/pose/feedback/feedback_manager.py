from ast import Return
import time

from .feedback_selector import FeedbackSelector
from ..models.feedback_item import FeedbackItem


class FeedbackManager:

    def __init__(self) -> None:
        self.selector = FeedbackSelector()

    def process(
        self,
        feedback_items: list[FeedbackItem],
    ) -> FeedbackItem | None:

        return self.selector.select(feedback_items)
      

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
    ) -> None :

        pass
