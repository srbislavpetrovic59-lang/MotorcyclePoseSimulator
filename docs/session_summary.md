# Session Summary
Design Principle

SessionSummary knows what happened during the ride.

Other components decide how to present those findings.

## Purpose

Session Summary transforms recorded session events into a clear,
useful and encouraging post-ride report.

It does not evaluate raw pose data and does not provide feedback
during the ride.

Its purpose is to help the rider understand:

- what went well,
- which posture issue appeared most often,
- where improvement was visible,
- what to focus on during the next session.


---
## Position in the Session subsystem

```text
FeedbackItem
      │
      ▼
SessionRecorder
      │
      ▼
list[SessionEvent]
      │
      ▼
SessionSummary
      │
      ▼
SessionReport
      │
      ├── Console
      ├── Unreal HUD
      ├── HTML
      ├── PDF
      └── SessionNarrator (future)
```

Session Summary is responsible only for transforming recorded events
into a structured report.

It is not responsible for presentation.
Presentation is handled by other components.
## Design Principles

- Human-first communication
- Positive reinforcement
- Focus on progress
- One clear recommendation
- Avoid information overload

---

## Input

Session Summary receives only:

- the session start and end times,
- a chronological list of SessionEvent objects.

It does not receive:

- camera frames,
- landmarks,
- raw joint angles,
- PoseEvaluator results,
- live FeedbackItem objects.

---

## Output

The result is a structured SessionReport.

The first version contains:

- session duration,
- most frequent issue,
- longest period without an active issue,
- one observed strength,
- one recommendation for the next ride.

---

## Initial Report

Version 1 should contain:

- Ride duration
- Most common posture issue
- Longest good posture period
- One recommendation

---

## Future Ideas

Possible future additions:

- Progress compared to previous rides
- Trend analysis
- Weekly reports
- Riding achievements
- Training recommendations

---

## Communication Style

The report should be:

- calm,
- specific,
- encouraging,
- honest,
- concise.

It should describe observations rather than judge the rider.

Prefer:

"Your posture became more stable during the second half of the ride."

Avoid:

"You made too many posture mistakes."

## Non-goals

The first version does not:

- assign scores,
- rank the rider,
- compare the rider with other users,
- diagnose physical or medical problems,
- answer free-form rider questions,
- change live coaching behavior,
- generate PDF or HTML reports.

## Workflow

Session Summary follows a simple three-step workflow:

1. Analyze recorded session events.
2. Extract objective facts.
3. Build a SessionReport.

The class does not interpret or present the report.
Its responsibility ends when the SessionReport is created.

## Initial Analysis

The initial implementation extracts only objective observations.

Current metrics:

- Session duration
- Most common issue
- Longest clear period

Future versions may include:

- observed strengths
- recommendations
- improvement trends

## Design Notes

SessionSummary performs deterministic analysis.

It should not:

- infer improvements that are not supported by events,
- generate motivational language,
- decide how results are presented.

These responsibilities belong to future presentation components.

SessionSummary transforms events into facts. It does not transform facts into language.