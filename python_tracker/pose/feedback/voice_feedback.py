from pose.models.feedback_item import FeedbackItem


class FeedbackSelector:

    @staticmethod
    def select(
        feedback: list[FeedbackItem],
    ) -> FeedbackItem | None:

        if not feedback:
            return None

        return max(
            feedback,
            key=lambda item: item.priority,
        )
