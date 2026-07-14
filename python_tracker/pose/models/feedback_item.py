from dataclasses import dataclass


@dataclass
class FeedbackItem:
    message: str
    priority: int
    voice: bool = True
    duration: float = 2.0
