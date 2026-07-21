from dataclasses import dataclass


@dataclass(frozen=True)
class SessionReport:
    duration: float
    most_frequent_message: str | None
    longest_clear_period_seconds: float