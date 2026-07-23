# Python–Unreal Communication Protocol

## Purpose

Defines the message format exchanged between the Python pose
analysis application and Unreal Engine.

The protocol allows Unreal Engine to receive already prepared
rider feedback without depending on Python implementation details.

## Transport

Messages are transmitted as UTF-8 encoded JSON objects over a
WebSocket connection.

Each WebSocket message contains exactly one JSON object.

## Message Types

### pose_feedback

Represents one rider coaching message.

```json
{
  "type": "pose_feedback",
  "timestamp": 12.4,
  "message": "Relax your shoulders",
  "severity": "gentle"
}
```

## Fields
### type

Message type identifier.

For coaching feedback, the value must be:

pose_feedback
timestamp

Number of seconds elapsed since the start of the riding session.

### Type:

'float'

### message

Human-readable coaching message prepared by the Python application.

Type:

'string'

Unreal Engine must display or present this message without changing
its meaning.

### severity

Controls how prominently Unreal Engine presents the message.

Initial supported values:

gentle
normal
important

The severity affects presentation only.

It must not change the meaning of the coaching message.

## Responsibilities
### Python

Python is responsible for:

- pose detection
- pose analysis
- evaluation
- feedback selection
- coaching behaviour
- message wording
- severity selection
- JSON serialization

### Unreal Engine

Unreal Engine is responsible for:

- receiving JSON messages
- validating required fields
- displaying messages
- choosing visual presentation based on severity
- logging malformed or unsupported messages

Unreal Engine must not reinterpret pose analysis results.

## Validation Rules

A valid `pose_feedback` message must contain:

- `type`
- `timestamp`
- `message`
- `severity`

Messages with missing required fields should be rejected and logged.

Unknown message types should be ignored and logged.

### Version 1 Scope

Version 1 supports only:

pose_feedback

The protocol does not yet include:

raw pose landmarks
joint rotations
session reports
connection status messages
command messages from Unreal to Python
binary data

## Acceptance criteria za postojeći issue

Možemo ih postaviti ovako:

## Design Principle

Python decides what the rider should be told.

Unreal Engine decides how that message is presented.
