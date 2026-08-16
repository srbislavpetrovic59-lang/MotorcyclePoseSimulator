# RiderState

## Purpose

`RiderState` is an immutable-style snapshot of the rider state
produced for a single analyzed frame.

It collects measurements and derived control states produced by
specialized analyzers.

`RiderState` does not perform analysis, event detection, or coaching.

Its responsibility is to provide a clean data model that can be:

- serialized
- recorded
- compared between frames
- converted into rider events
- transmitted to Unreal Engine

## Position in the Architecture

Camera
   │
   ▼
Pose / Hand Detectors
   │
   ▼
Specialized Analyzers
   │
   ▼
PoseAnalyzer
   │
   ▼
RiderStateMapper
   │
   ▼
RiderState
   │
   ├── RiderEventDetector
   ├── SessionRecorder
   └── WebSocket / Unreal Engine

## Design Principle

`RiderState` is a data container.

It must not calculate geometry or decide whether rider behavior is
good or bad.

Those responsibilities belong to:

- analyzers for measurements
- predicates / recognizers for state interpretation
- RiderEventDetector for transitions
- PoseCoach for coaching

This keeps the model simple and prevents business logic from becoming
embedded inside the transport structure.

## Current Measurements

### Head

- `head_roll`
- `head_yaw_ratio`
- `head_forward`

### Arms

- `left_elbow_angle`
- `right_elbow_angle`

### Hands

- `left_hand_detected`
- `right_hand_detected`
- `left_hand_rotation`
- `right_hand_rotation`

### Clutch

- `clutch_progress`
- `clutch_in_friction_zone`

`clutch_progress` may be `None` when the required hand geometry is
unavailable.

A missing measurement is intentionally different from:

`clutch_progress == 0.0`

which represents a valid released-clutch position.

### Front Brake

- `front_brake_progress`
- `front_brake_active`

`front_brake_progress` may be `None` when the right-hand measurement
is unavailable.

`front_brake_active` is derived using hysteresis to avoid unstable
state changes near the activation threshold.

### Throttle

- `throttle_progress`
- `throttle_active`

`throttle_progress` represents the calibrated throttle position:

0.0 = throttle closed

1.0 = throttle fully open

Intermediate values represent intermediate throttle rotation.

The throttle measurement supports circular angle wraparound and uses
live calibration.

Calibration can be changed during operation and is persisted between
sessions.

### Legs

- `left_knee_angle`
- `right_knee_angle`
- `left_foot_angle`
- `right_foot_angle`

### Body

- `torso_angle`

### Tracking Quality

- `pose_confidence`

## Missing Measurements

Some measurements may temporarily be unavailable because of:

- hand occlusion
- MediaPipe detection loss
- insufficient landmark confidence
- incomplete control calibration

For continuous hand controls, `None` means:

> the control position is currently unknown

It must never automatically be interpreted as zero.

This distinction is important because detection loss must not create
false control events.

For example:

friction zone → hand lost

must not be interpreted as:

clutch released

and:

front brake active → hand lost

must not be interpreted as:

front brake released

## Rider Events

`RiderState` represents state.

`RiderEventDetector` compares consecutive valid states and produces
transitions such as:

- clutch friction zone reached
- clutch released from friction zone
- clutch pulled from friction zone
- front brake applied
- front brake released
- throttle opened
- throttle closed

Detection loss is not treated as a rider action.

## Serialization

`RiderState` can be serialized to JSON for transport.

The JSON representation is used by the WebSocket output layer and
consumed by Unreal Engine.

This keeps the Python analysis layer independent from Unreal-specific
code.

## Unreal Engine

The Unreal C++ side contains a corresponding `FRiderState`.

Python remains responsible for measurement and interpretation.

Unreal receives the resulting state and can use it for:

- visualization
- Blueprint events
- HUD elements
- avatar behavior
- future simulation logic

The transport boundary should not duplicate analysis rules unless
required for presentation or event exposure.

## Future Extensions

Possible future fields include:

- rear brake progress/state
- gear
- additional finger metrics
- richer control confidence values
- control calibration metadata

New fields should be added only when the underlying measurement or
state has actually been implemented.