# Hand Control Design

## Purpose

`HandControlAnalyzer` analyzes rider interaction with
motorcycle hand controls.

Its responsibility is to measure objective hand-related
geometry and derive normalized control metrics.

It never determines riding quality and never produces
coaching feedback.

## Position in the Architecture

Camera
      │
      ├── Pose Detector
      └── Hand Detector
              │
              ▼
     HandControlAnalyzer
              │
              ▼
         PoseAnalyzer
              │
              ▼
          RiderState
              │
              ▼
     RidingStateRecognizer
              │
              ▼
          PoseCoach

## Input

`HandControlAnalyzer` receives hand landmarks detected by
MediaPipe Hands.

Handedness information is used to distinguish the left and
right hand.

## Responsibilities

`HandControlAnalyzer` currently measures geometry related to:

- clutch control
- front brake control
- throttle control
- left and right hand rotation
- finger geometry required by individual controls

It converts raw hand geometry into objective control metrics.

It does not interpret whether the rider is riding correctly.

## Normalized Control Progress

Continuous motorcycle controls are represented using a
normalized progress value:

0.0 = control at its calibrated starting position

1.0 = control at its calibrated end position

Values between 0.0 and 1.0 represent intermediate control
positions.

A progress value may be `None` when the required hand
geometry is unavailable or the control is not calibrated.

## Clutch

Clutch analysis uses left-hand geometry.

The analyzer can expose a normalized clutch progress and
detect whether the clutch is inside the friction zone.

The clutch model is designed to support gradual control
movement rather than only binary pressed/released states.

## Front Brake

Front brake analysis uses right index finger geometry.

The analyzer exposes:

- front brake progress
- front brake active state

The active state uses hysteresis so that small measurement
variations near the activation threshold do not repeatedly
switch the brake between active and inactive.

Transitions can later be represented as rider events such as:

- front brake applied
- front brake released

## Throttle

Throttle analysis uses right-hand rotation.

The analyzer exposes a normalized:

`throttle_progress`

where:

0.0 = throttle closed

1.0 = throttle fully open

### Circular Angle Geometry

Hand rotation is a circular quantity.

For example:

359 degrees and 4 degrees represent nearby physical
orientations even though their numeric values are far apart.

Throttle progress therefore uses signed angular differences
and explicitly handles the 0/360 degree wraparound.

The calculation also handles the 180 degree boundary used by
some calibrated throttle ranges.

## Throttle Calibration

Throttle endpoints are calibrated from live hand geometry.

During live operation:

`C` captures the closed-throttle position.

`O` captures the fully-open throttle position.

The calibration is not permanent or locked.

The rider can repeat either calibration at any time to adapt
to a different camera position, rider position, motorcycle,
or hand orientation.

## Persistent Throttle Calibration

The most recently captured throttle calibration is persisted
to a JSON file.

On startup:

- an existing calibration is loaded automatically
- if no calibration file exists, the analyzer starts
  uncalibrated
- throttle progress remains unavailable until both endpoints
  are known

When `C` or `O` is captured again, the corresponding
calibration value is updated and the new calibration is
saved.

Persistence therefore provides convenient startup behavior
without preventing later recalibration.

## Missing Hand Data

Hand landmarks may temporarily disappear because of
occlusion or detector uncertainty.

Missing geometry must not be interpreted as control movement.

When the geometry required for a metric is unavailable, the
corresponding progress value may be `None`.

This prevents a lost hand from being interpreted as a
released brake, closed throttle, or another physical control
transition.

## Design Principles

- Measure observable geometry only.
- Never perform coaching inside the analyzer.
- Never estimate rider intention.
- Prefer continuous control metrics where meaningful.
- Preserve an explicit distinction between zero and invalid
  measurement.
- Handle circular hand rotation explicitly.
- Use calibration instead of assuming universal hand angles.
- Allow calibration to be repeated when riding or camera
  conditions change.
- Keep control measurement separate from rider-event
  detection and coaching.