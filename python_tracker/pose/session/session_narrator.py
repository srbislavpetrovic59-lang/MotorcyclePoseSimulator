class SessionNarrator:
    def narrate(self, report: SessionReport) -> str:
        parts = [
            self._describe_duration(report.duration),
            self._describe_issue(report.most_common_issue),
            self._describe_clear_period(
                report.longest_clear_period_seconds
            ),
        ]

        return " ".join(parts)