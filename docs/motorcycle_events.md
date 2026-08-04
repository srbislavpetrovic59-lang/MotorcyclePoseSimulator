# Motorcycle Events

Motorcycle events describe rider interaction with the motorcycle.

Unlike perception events, motorcycle events are inferred from
multiple observable measurements or primitive events.

## Primitive Motorcycle Events

- LOOKING_AHEAD
- CLUTCH_FRICTION_ZONE_REACHED
- THROTTLE_OPENED
- REAR_BRAKE_RELEASED

## Derived Motorcycle Events

- READY_TO_START
- RIDE_STARTED

# Motorcycle Events

## Purpose

Motorcycle events describe meaningful rider interaction with the
motorcycle.

Unlike perception events, motorcycle events are inferred from
multiple observable measurements or primitive events.

They represent riding actions rather than raw sensor observations.

## Event Categories

### Primitive Motorcycle Events

Primitive motorcycle events are directly observable from rider
measurements.

Examples:

- LOOKING_AHEAD
- CLUTCH_FRICTION_ZONE_REACHED
- THROTTLE_OPENED
- REAR_BRAKE_RELEASED

### Derived Motorcycle Events

Derived motorcycle events are inferred from multiple primitive
events.

Examples:

- READY_TO_START
- RIDE_STARTED

## Design Principle

Motorcycle events should be built from simpler observable events.

Complex riding behavior should never be inferred directly from
raw measurements when it can be expressed as a combination of
primitive events.
Every derived motorcycle event should be explainable by the primitive
events that caused it.


## Initial Development Order

1. LOOKING_AHEAD
2. CLUTCH_FRICTION_ZONE_REACHED
3. THROTTLE_OPENED
4. REAR_BRAKE_RELEASED
5. READY_TO_START
6. RIDE_STARTED