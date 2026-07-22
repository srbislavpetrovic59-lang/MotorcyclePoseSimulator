# Session Narrator

## Purpose

SessionNarrator transforms objective analysis into human-friendly feedback.

It explains the results of a riding session using clear,
supportive, and encouraging language.

The narrator never changes or reinterprets the facts contained
in the SessionReport.

Its responsibility is communication, not analysis.

## Position in the Architecture

SessionEvent
      ↓
SessionRecorder
      ↓
SessionSummary
      ↓


SessionReport
      ↓
SessionNarrator
      ↓
Narration
       │
       ├── Console
       ├── Unreal HUD
       ├── Mobile App
       ├── PDF Report
       └── Voice Assistant


## Responsibility

Transforms a SessionReport into natural language feedback.

## Input

SessionReport
SessionNarrator receives a completed SessionReport.

The report contains the objective results of the riding session,
such as:

- session duration
- most common issue
- longest clear period

## Output

Narration (not yet a class)
The output is a human-readable narration represented as a string.
Version 1 does not introduce a separate Narration class.

Example:

"You completed a 60-second riding session.
Your most frequent posture issue was relaxing your shoulders.
Your longest period with correct posture was 25 seconds."

## Example

Input:

- duration: 600 s
- most common issue: Relax your shoulders
- longest clear period: 120 s

Output:

You completed a 10-minute riding session.
Your most common posture issue was shoulder tension.
Your longest uninterrupted period with correct posture was two minutes.

## Public Interface

SessionNarrator exposes one main operation:

narrate(report: SessionReport) -> str

The method converts the structured report into rider-friendly text.

## Behavior Rules

SessionNarrator should:

- preserve all facts from the SessionReport
- use clear and supportive language
- avoid technical implementation details
- avoid inventing information
- handle missing values gracefully
- remain independent of the output platform
- produce grammatically correct output when optional values are missing
- avoid mentioning unavailable report fields
- keep wording deterministic for identical input

## Version 1 Scope

The first version of SessionNarrator:

- produces one textual summary
- uses deterministic templates
- supports the current SessionReport fields
- does not use artificial intelligence or external services
- does not produce voice output directly

## Design Principles

SessionNarrator is responsible only for communication.

It must never:

- analyze posture
- modify SessionReport values
- infer new conclusions
- access SessionRecorder directly
- access PoseAnalyzer directly

All riding analysis must be completed before narration begins.

Camera
    │
    ▼
PoseDetector
    │
    ▼
PoseAnalyzer
    │
    ▼
PoseEvaluator
    │
    ▼
FeedbackManager
    │
    ▼
SessionRecorder
    │
    ▼
SessionSummary
    │
    ▼
SessionReport
    │
    ▼
══════════════════════════════════════
        Analysis ends here
══════════════════════════════════════
    │
    ▼
SessionNarrator
    │
    ▼
Narration