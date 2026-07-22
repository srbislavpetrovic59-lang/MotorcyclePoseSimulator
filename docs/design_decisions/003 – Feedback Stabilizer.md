\# Design Decisions



This document captures the major architectural and design decisions made during the project's evolution.



Unlike the CHANGELOG, which records \*what\* changed, this document explains \*why\* those changes were made.



Each decision has a stable identifier (DD-XXX) to make it easy to reference from documentation, issues, and commit messages.

## Status

Planned

## Problem

Raw posture feedback changes rapidly because of landmark jitter.

This causes unstable transitions for downstream components.

## Decision

Introduce a FeedbackStabilizer between FeedbackManager
and all feedback consumers.

## Consequences

### Positive

- Stable coaching
- Stable session recording
- Better user experience

### Negative

- One additional processing component
- Small delay before feedback changes

## Alternatives Considered

- Stabilize inside PoseCoach
- Stabilize inside SessionRecorder

Rejected because stabilization is a shared responsibility.