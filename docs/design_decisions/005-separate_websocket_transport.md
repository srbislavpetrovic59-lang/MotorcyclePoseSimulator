# 005 – Separate WebSocket Transport (## 2026-07-23)

## Status

Accepted

## Context

The project needs to send coaching messages from Python to Unreal
Engine.

The communication mechanism should not become coupled to the Output
layer.

## Decision

Introduce a dedicated `WebSocketClient` responsible only for
transport.

`UnrealOutput` prepares protocol messages and delegates transmission
to `WebSocketClient`.

## Consequences

### Positive

- Output and transport remain independent.
- Transport can be replaced without changing Output.
- Easier testing using mocks.

### Negative

- One additional abstraction.