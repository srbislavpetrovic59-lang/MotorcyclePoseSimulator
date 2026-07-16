# Motorcycle Pose Simulator

The application detects the rider’s pose, calculates body metrics, evaluates riding posture and provides prioritized visual feedback.

Real-time motorcycle riding posture simulator using computer vision, MediaPipe, WebSocket communication and Unreal Engine 5.

## Goal

The goal of this project is to track rider body posture using a camera, analyze riding-related body movements, and visualize the rider on a motorcycle in Unreal Engine.

The project is intended both as a technical portfolio project and as a foundation for a future motorcycle riding coach.

Before running the application, update CAMERA_URL in config.py
to match your local IP Webcam address.
## Current Features

- Real-time pose detection using MediaPipe
- Rider skeleton rendering
- Elbow and knee angle measurement
- Torso angle and shoulder tilt analysis
- Arm and leg symmetry calculation
- Rider posture scoring
- Prioritized feedback selection
- Feedback cooldown management
- OpenCV HUD overlay
- Modular analysis and evaluation pipeline

## Project Status

The project is under active development.

The current Python prototype supports real-time pose analysis, posture evaluation and visual coaching feedback. Voice coaching, calibration, session statistics and Unreal Engine integration are planned.

## Architecture

```text
Camera / IP Webcam
        │
        ▼
Pose Detector
        │
        ▼
Pose Analyzer
        │
        ├── ArmAnalyzer
        ├── BodyAnalyzer
        ├── FootAnalyzer
        │
        ▼
Pose Metrics
        │
        ▼
Pose Evaluator
        │
        ▼
Feedback Manager
        │
        ├── Feedback Selector
        ├── Overlay Renderer
        └── (Voice Coach - planned)
        │
        ▼
OpenCV HUD
        │
        ▼
(Unreal Engine integration - planned)
```

## Planned Features

- Voice coaching
- Rider calibration
- Session recording and statistics
- Unreal Engine integration
- WebSocket telemetry
- Configurable coaching profiles
