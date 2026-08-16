# Python–Unreal Communication Protocol

## Purpose

Defines the communication boundary between the Python rider-analysis
application and Unreal Engine.

Python performs detection, measurement, and control-state analysis.

Unreal Engine receives prepared rider state and exposes it to the
visualization and Blueprint layers.

The protocol prevents Unreal Engine from depending on Python
implementation details.

## Transport

Messages are transmitted as UTF-8 encoded JSON objects over a
WebSocket connection.

Each WebSocket message contains one serialized rider-state snapshot.

## Direction

The current protocol is primarily:

Python → Unreal Engine

Python produces analyzed rider state.

Unreal Engine consumes that state.

Bidirectional control messages are not currently part of the protocol.

## RiderState Message

The main real-time message contains the current rider state.

Example:

```json
{
  "head_roll": -4.2,
  "head_yaw_ratio": -0.1,

  "left_elbow_angle": 148.0,
  "right_elbow_angle": 152.7,

  "left_knee_angle": 170.0,
  "right_knee_angle": 168.0,

  "left_foot_angle": 145.0,
  "right_foot_angle": 142.0,

  "torso_angle": 89.5,
  "pose_confidence": 0.92,

  "clutch_progress": null,
  "clutch_in_friction_zone": false,

  "front_brake_progress": 0.35,
  "front_brake_active": true,

  "throttle_progress": 0.45,
  "throttle_active": true
}

The exact serialized field names are defined by the Python
RiderState model and must remain compatible with the Unreal
FRiderState parser.

Missing Measurements

A missing continuous measurement is represented as:

null

This is intentionally different from:

0.0

For example:

"throttle_progress": null

means that the throttle position is currently unknown.

"throttle_progress": 0.0

means that a valid measurement indicates a closed throttle.

Unreal Engine must preserve this distinction.

Detection loss must not be interpreted as physical control movement.

Clutch

The current protocol can expose:

clutch_progress
clutch_in_friction_zone

clutch_progress is a normalized continuous value when valid.

The friction-zone state is derived by Python.

Unreal Engine must not independently recalculate the friction zone.

Front Brake

The current protocol exposes:

front_brake_progress
front_brake_active

front_brake_progress represents the normalized brake-control
measurement.

front_brake_active is derived by Python using the current control
logic and hysteresis.

Unreal Engine consumes this state rather than reproducing the
front-brake analysis.

Throttle

The current protocol exposes:

throttle_progress
throttle_active

throttle_progress is normalized:

0.0 = throttle closed

1.0 = throttle fully open

Intermediate values represent intermediate throttle opening.

Throttle calibration and circular-angle handling are Python
responsibilities.

throttle_active is also determined by Python.

Unreal Engine must not duplicate throttle calibration or hysteresis
logic.

Unreal RiderState

The Unreal C++ layer contains a corresponding FRiderState.

UPoseWebSocketComponent receives each WebSocket message, parses the
JSON representation, and populates FRiderState.

The component can then expose selected state and transitions to
Blueprint.

Blueprint Events

Unreal may expose state transitions as Blueprint events.

Current examples include:

front brake applied
front brake released

Additional events can be exposed as required by the visualization
layer.

Event exposure in Unreal must not change the underlying measurement
meaning defined by Python.

Responsibilities
Python

Python is responsible for:

pose detection
hand detection
geometric measurement
control calibration
normalized control progress
hysteresis
rider-state construction
event interpretation where applicable
coaching logic
JSON serialization
Unreal Engine

Unreal Engine is responsible for:

maintaining the WebSocket connection
receiving JSON messages
validating and parsing supported fields
exposing rider state to C++ and Blueprint
visualization
HUD presentation
avatar behavior
logging malformed or unsupported data

Unreal Engine must not reinterpret raw pose or hand geometry when the
corresponding state has already been prepared by Python.

Validation

A malformed JSON message must be rejected and logged.

Missing optional measurements must remain invalid rather than being
silently converted into physical zero values.

Unknown fields should not prevent otherwise compatible RiderState
messages from being processed.

Compatibility

Python RiderState serialization and Unreal FRiderState parsing form
a protocol boundary.

When a new field is introduced, the preferred implementation order is:

measurement or state implemented in Python
Python RiderState updated
serialization covered by tests
Unreal FRiderState updated
Unreal JSON parser updated
live WebSocket communication verified

This prevents documentation or Unreal code from getting ahead of the
actual analysis implementation.

Future Extensions

Possible future protocol additions include:

rear brake state
gear state
additional hand-control metrics
session summaries
coaching messages
connection/status messages
Unreal-to-Python commands

These should be added only when the corresponding feature is actually
implemented.

Design Principle

Python decides what the rider state means.

Unreal Engine decides how that state is visualized and presented.