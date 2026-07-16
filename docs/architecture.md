```mermaid
flowchart TD

    Camera --> PoseDetector
    PoseDetector --> PoseAnalyzer

    PoseAnalyzer --> ArmAnalyzer
    PoseAnalyzer --> BodyAnalyzer
    PoseAnalyzer --> FootAnalyzer

    PoseAnalyzer --> PoseMetrics

    PoseMetrics --> PoseEvaluator

    PoseEvaluator --> FeedbackManager

    FeedbackManager --> OverlayRenderer
    FeedbackManager --> VoiceCoach

    OverlayRenderer --> OpenCV
```