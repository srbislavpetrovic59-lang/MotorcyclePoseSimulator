\# Design Decisions



This document captures the major architectural and design decisions made during the project's evolution.



Unlike the CHANGELOG, which records \*what\* changed, this document explains \*why\* those changes were made.



Each decision has a stable identifier (DD-XXX) to make it easy to reference from documentation, issues, and commit messages.

## 

## DD-001 – PoseAnalyzer as an Orchestrator

### Decision

PoseAnalyzer coordinates specialized analyzers instead of implementing posture calculations directly.

### Motivation

As the project grew, a single analyzer became difficult to maintain. Splitting responsibilities into ArmAnalyzer, BodyAnalyzer and FootAnalyzer improved readability and extensibility.

### Consequences

* Easier testing
* Clear responsibilities
* Simpler future extensions



DD-002

Separate coaching strategy from feedback generation.

DD-003

PoseCoach communicates only persistent feedback.

