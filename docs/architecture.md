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