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

## Acceptance criteria za postojeći issue

Možemo ih postaviti ovako:

```markdown
## Acceptance Criteria

- transport is defined
- JSON encoding is defined
- `pose_feedback` message structure is documented
- every field has a clear type and responsibility
- supported severity values are documented
- malformed and unknown messages have defined behaviour
- Python and Unreal responsibilities are separated
- version 1 scope and exclusions are documented
