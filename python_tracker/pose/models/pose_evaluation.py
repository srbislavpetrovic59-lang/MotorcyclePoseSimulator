from dataclasses import dataclass
from pose.models.feedback_item import FeedbackItem


@dataclass
class PoseEvaluation:

    score: int

    rider_state: str

    feedback: list[FeedbackItem]