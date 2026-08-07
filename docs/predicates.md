# Predicates

## Purpose

Predicates describe the current rider state.

A predicate is a boolean value derived from one or more
measurements.

Unlike events, predicates do not represent changes.

They describe what is true **right now**.

---

## Position in the Architecture

Measurements
      ↓
Predicates
      ↓
Primitive Events
      ↓
Derived Events

---

## Responsibility

Predicates transform continuous measurements into
meaningful rider states.

They contain no temporal logic.

They are independent from event detection.

---

## Examples

### head_forward

Derived from:

- head_roll
- head_yaw_ratio

Meaning:

The rider is looking approximately forward.

---

### throttle_open

Derived from:

- right_hand_rotation

Meaning:

The rider has rotated the throttle beyond
the configured threshold.

---

### left_rotation_active

Derived from:

- left_hand_rotation

Meaning:

The left hand has rotated beyond the configured
threshold.

This predicate intentionally avoids motorcycle-specific
terminology.

After sufficient experimental validation it may evolve into:

- clutch_in_friction_zone

---

## Relationship to Events

Events detect changes in predicates.

Example

```
False → True
```

becomes

```
THROTTLE_OPENED
```

Predicates never emit events directly.

This responsibility belongs exclusively to
RiderEventDetector.

## Design Principles

Predicates

- are deterministic
- have no memory
- do not emit events
- do not know previous states
- are computed every frame

---

Events are responsible for detecting transitions.

Example

False → True

becomes

THROTTLE_OPENED

Predicates themselves never emit events.

---

## Philosophy

Measurements answer:

"What does the camera measure?"

Predicates answer:

"What is currently true?"

Events answer:

"What has just changed?"

Derived events answer:

"What does this mean for the rider?"