# RiderEventDetector

## Purpose

RiderEventDetector transforms RiderState into
meaningful riding events.

It never evaluates riding quality.

It never provides coaching.

Its only responsibility is recognizing
what the rider is doing.


RiderEventDetector is stateful.

It keeps minimal history required
to recognize riding events.




## Non-Responsibilities

RiderEventDetector does NOT:

- evaluate riding quality,
- provide rider feedback,
- interpret rider skill,
- access MediaPipe landmarks directly,
- generate natural language.

Those responsibilities belong to other components.


I sada mi se rodila još jedna ideja...

Možda RiderEventDetector uopšte neće biti samo jedan detector.

Možda će jednog dana izgledati ovako:

RiderEventDetector
│
├── PerceptionEventDetector
└── RidingEventDetector

Ali... ne sada.

## Event Emission Rule

An event is emitted only when a state changes.

If a state remains unchanged,
no new event is emitted.

## Scenario: Pose Acquired

Given

The previous RiderState has no valid pose.

When

The current RiderState contains a valid pose.

Then

Emit a single POSE_ACQUIRED event.

## Scenario: Pose Remains Available

Given

The previous RiderState contains a valid pose.

When

The current RiderState also contains a valid pose.

Then

Emit no event.

              confidence

      < threshold        ≥ threshold

           OFF ─────────────► ON
               POSE_ACQUIRED

           ON ─────────────► OFF
                 POSE_LOST