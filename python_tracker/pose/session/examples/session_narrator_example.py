from ..session_report import SessionReport
from ..session_narrator import SessionNarrator


report = SessionReport(
    duration=600,
    most_frequent_message="Relax your shoulders.",
    longest_clear_period_seconds=125,
)

narrator = SessionNarrator()

print(narrator.narrate(report))