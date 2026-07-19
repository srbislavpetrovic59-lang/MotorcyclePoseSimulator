from dataclasses import dataclass
from enum import Enum


class SessionEventType(Enum):
    ISSUE_STARTED = "issue_started"
    ISSUE_RESOLVED = "issue_resolved"


@dataclass(frozen=True)
class SessionEvent:
    event_type: SessionEventType
    message: str
    timestamp: float