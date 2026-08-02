
# Rider Events

## Purpose

RiderEventDetector transforms continuous measurements into meaningful
riding events.

It does not evaluate riding quality.

It does not provide coaching.

Its only responsibility is recognizing what the rider is currently doing.

Examples:

- RideStarted
- ClutchReleased
- GearShiftStarted
- CornerEntry
- BrakingStarted


RideStarted

RideStopped

ClutchPulled

ClutchReleased

ThrottleOpened

ThrottleClosed

FrontBrakeStarted

FrontBrakeReleased

RearBrakeStarted

RearBrakeReleased

GearShiftStarted

GearShiftCompleted

CornerEntry

CornerExit


POSE_ACQUIRED is emitted when the system transitions from 
"pose unavailable" to "pose available".