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