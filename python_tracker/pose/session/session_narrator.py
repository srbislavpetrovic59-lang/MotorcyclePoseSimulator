from __future__ import annotations
from .session_report import SessionReport


class SessionNarrator:
    """Transforms a SessionReport into rider-friendly text."""

    def narrate(self, report: SessionReport) -> str:
        if report is None:
            raise ValueError("report must not be None")

        sentences: list[str] = []
        
        message = self._narrate_most_frequent_message(report)
        
        if message:
            sentences.append(message)
        
        duration_text = self._format_duration(report.duration)
        
        
        if duration_text is not None:
            sentences.append(
                f"You completed a riding session lasting {duration_text}."
            )

       
        clear_period_text = self._format_duration(
            report.longest_clear_period_seconds
        )
        if clear_period_text is not None:
            sentences.append(
                f"Your longest uninterrupted period with correct posture "
                f"was {clear_period_text}."
            )

        if not sentences:
            return "The session was completed, but no summary data is available."

        return " ".join(sentences)

    @staticmethod
    def _format_duration(seconds: float | int | None) -> str | None:
        if seconds is None or seconds < 0:
            return None

        rounded_seconds = round(seconds)

        if rounded_seconds < 60:
            unit = "second" if rounded_seconds == 1 else "seconds"
            return f"{rounded_seconds} {unit}"

        if rounded_seconds % 60 == 0:
            minutes = rounded_seconds // 60
            unit = "minute" if minutes == 1 else "minutes"
            return f"{minutes} {unit}"

        minutes, remaining_seconds = divmod(rounded_seconds, 60)

        minute_unit = "minute" if minutes == 1 else "minutes"
        second_unit = "second" if remaining_seconds == 1 else "seconds"

        return (
            f"{minutes} {minute_unit} and "
            f"{remaining_seconds} {second_unit}"
        )

    def _narrate_most_frequent_message(
        self,
        report: SessionReport,
    ) ->  str | None:
        if not report.most_frequent_message:
                return None

        message = self._normalize_message(report.most_frequent_message)

        return (
            f'Your most frequent coaching message was '
            f'"{message}".'
        )

    @staticmethod
    def _normalize_message(message: str) -> str:
        normalized = message.strip()

        if not normalized:
            return normalized

        normalized = normalized[0].lower() + normalized[1:]
        return normalized.rstrip(".")
