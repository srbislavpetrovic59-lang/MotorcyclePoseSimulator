# Motorcycle Pose Simulator Architecture

The application is organized as a real-time processing pipeline.

```mermaid
flowchart TD

    Camera[Camera]
    PoseDetector[PoseDetector]
    HandDetector[HandDetector]

    Pipeline[PosePipeline]

    ArmAnalyzer[ArmAnalyzer]
    BodyAnalyzer[BodyAnalyzer]
    FootAnalyzer[FootAnalyzer]

    Evaluator[PoseEvaluator]
    FeedbackManager[FeedbackManager]
    PoseCoach[PoseCoach]

    Mapper[RiderStateMapper]
    RiderState[RiderState]

    Recorder[SessionRecorder]
    Summary[SessionSummary]
    Narrator[SessionNarrator]

    Dispatcher[OutputDispatcher]
    Console[ConsoleOutput]

    WebSocket[WebSocketServer]
    Unreal[Unreal Engine<br/>PoseWebSocketComponent / BP_PoseReceiver]

    Camera --> PoseDetector
    Camera --> HandDetector

    PoseDetector --> Pipeline
    HandDetector --> Pipeline

    Pipeline --> ArmAnalyzer
    Pipeline --> BodyAnalyzer
    Pipeline --> FootAnalyzer

    ArmAnalyzer --> Evaluator
    BodyAnalyzer --> Evaluator
    FootAnalyzer --> Evaluator

    Evaluator --> FeedbackManager
    FeedbackManager --> PoseCoach

    ArmAnalyzer --> Mapper
    BodyAnalyzer --> Mapper
    FootAnalyzer --> Mapper

    Mapper --> RiderState

    RiderState --> Recorder
    RiderState --> WebSocket

    Recorder --> Summary
    Summary --> Narrator

    PoseCoach --> Dispatcher
    Narrator --> Dispatcher

    Dispatcher --> Console

    WebSocket --> Unreal



    Architectural Responsibilities
Input

Camera provides video frames to the real-time pipeline.

PoseDetector extracts body landmarks.

HandDetector extracts hand landmarks used for motorcycle control analysis.

Analysis

Analysis is divided by responsibility:

ArmAnalyzer — arm and elbow posture
BodyAnalyzer — torso and head posture
FootAnalyzer — legs, feet and rear-brake state

Analyzers produce measurements and state. They do not decide how feedback is presented to the rider.

Rider State

RiderStateMapper converts analysis results into the transport-neutral RiderState model.

RiderState represents the current measured state of the rider and motorcycle controls.

This separation keeps pose analysis independent from Unreal Engine and other output systems.

Feedback

PoseEvaluator evaluates analyzed posture.

FeedbackManager manages feedback items.

PoseCoach controls how and when feedback is presented.

PoseCoach follows the design principle of behaving like a calm riding instructor rather than an alarm system.

Session

SessionRecorder records relevant events during a riding session.

SessionSummary converts recorded events into session-level information.

SessionNarrator transforms that information into human-friendly feedback without changing the underlying facts.

Output

OutputDispatcher distributes feedback to available output implementations.

ConsoleOutput provides the current console output.

Additional outputs can be added without changing the analysis layer.

Unreal Engine Integration

WebSocketServer transports serialized RiderState data to Unreal Engine.

Unreal Engine receives the state through UPoseWebSocketComponent, where it can be consumed by BP_PoseReceiver and later by HUD, animation and simulation systems.

Design Principle

The architecture separates:

measurement → state → evaluation → feedback → presentation

Tracking loss is treated as missing information, not automatically as a change of rider state.

This is especially important for stateful controls such as the rear brake, where temporary landmark loss must not generate false control events.