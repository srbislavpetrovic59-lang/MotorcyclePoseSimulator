# DD-00X - User-defined Ride Focus

## Status
Deferred

## Problem

Riders often have a specific concern that may not appear naturally during a ride.

## Decision

The initial version will analyze only objectively observed posture events.
User-defined focus areas are intentionally excluded.

## Rationale

- Keeps SessionSummary independent of session setup.
- Avoids coupling coaching logic with user preferences.
- Allows the coaching pipeline to mature before personalization.

## Future Direction

Introduce a RideSession object containing:
- user goal
- optional notes
- session metadata