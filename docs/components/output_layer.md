## Purpose

Output Layer is responsible for presenting information.

It never performs analysis.

It never modifies SessionReport.

It only transforms information into platform-specific output.

## Position in the Architecture

Camera
    ↓
PoseDetector
    ↓
PoseAnalyzer
    ↓
PoseEvaluator
    ↓
PoseCoach
    ↓
SessionRecorder
    ↓
SessionSummary
    ↓
SessionReport
    ↓
SessionNarrator
    ↓
Output Layer


SessionReport
      │
      ▼
SessionNarrator
      │
      ▼
OutputDispatcher
      │
 ┌────┼────┬──────┬──────┐
 ▼    ▼    ▼      ▼      ▼
HUD Voice PDF Console Mobile

## Responsibilities

Output Layer is responsible for presenting narration.

It never:
- performs analysis
- evaluates posture
- modifies SessionReport
- generates coaching advice


## Supported Outputs

Console

Unreal HUD

Voice

Mobile

PDF

## Design Philosophy

Output Layer is the final stage of the coaching pipeline.

It is intentionally isolated from pose analysis,
evaluation and narration.

Its only responsibility is presentation.

