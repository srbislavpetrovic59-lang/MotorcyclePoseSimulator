@dataclass(frozen=True)
class SessionReport:
    duration_seconds: float
    most_common_issue: str | None
    longest_clear_period_seconds: float
    strength: str
    recommendation: str